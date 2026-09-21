"""Read-only maintenance commands for wm-notecards projects."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Iterator

FindingKind = Literal["local-helper", "legacy-theme", "vendored-runtime", "duplicate-notebook"]
# Keep this list explicit: the doctor is a migration aid, not a Python-code search engine.
# These are the public helpers most often copied into older notebooks and then allowed
# to drift away from the package implementation.
_HELPER_MARKERS = (
    "def question_card(",
    "def preview_card(",
    "def takeaway_card(",
    "def verdict_card(",
    "def next_think_card(",
    "def display_cols_by_dtype(",
    "def display_dtype_change_chips(",
    "def display_data_chips(",
    "def wm_eda_overview(",
    "def wm_render_styler(",
    "def wm_render_figure_card(",
    "def wm_formula_card(",
    "class WMTheme",
)
_IGNORED_PARTS = {
    ".git",
    ".ipynb_checkpoints",
    ".venv",
    ".webapp-tester",
    "node_modules",
    "outputs",
    "build",
}


@dataclass(frozen=True, slots=True)
class DoctorFinding:
    """A location where a project can drift from the canonical runtime."""

    kind: FindingKind
    path: str
    cell: int | None
    detail: str


def _is_ignored(path: Path) -> bool:
    return bool(_IGNORED_PARTS & set(path.parts))


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _scan_notebook(path: Path, root: Path) -> list[DoctorFinding]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    findings: list[DoctorFinding] = []
    for index, cell in enumerate(payload.get("cells", [])):
        source = cell.get("source", "")
        text = "".join(source) if isinstance(source, list) else str(source)
        markers = [marker.rstrip("(") for marker in _HELPER_MARKERS if marker in text]
        if markers:
            findings.append(
                DoctorFinding(
                    "local-helper",
                    _relative(path, root),
                    index,
                    f"Defines canonical helper(s): {', '.join(markers)}",
                )
            )
    return findings


def _project_files(root: Path) -> Iterator[Path]:
    """Prune generated directories before traversing their contents."""
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in _IGNORED_PARTS)
        for name in sorted(files):
            path = Path(directory) / name
            if not path.is_symlink() and path.is_file():
                yield path


def scan_project(root: Path) -> list[DoctorFinding]:
    """Inspect a project without reading notebook outputs or changing files."""
    resolved = root.resolve()
    if not resolved.is_dir():
        raise ValueError(f"Project root is not a directory: {resolved}")
    findings: list[DoctorFinding] = []
    for path in _project_files(resolved):
        if path.name == "wm_theme.py":
            findings.append(
                DoctorFinding("legacy-theme", _relative(path, resolved), None, "Legacy theme module")
            )
        if path.name == "__init__.py" and "_vendor/wm_notecards" in path.as_posix():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            findings.append(
                DoctorFinding(
                    "vendored-runtime",
                    _relative(path.parent, resolved),
                    None,
                    f"Vendored package manifest sha256:{digest}",
                )
            )
        if path.suffix == ".ipynb":
            findings.extend(_scan_notebook(path, resolved))
            if "colab" in path.stem.casefold():
                findings.append(
                    DoctorFinding(
                        "duplicate-notebook",
                        _relative(path, resolved),
                        None,
                        "Colab-named notebook; verify it is generated from a canonical source",
                    )
                )
    return sorted(findings, key=lambda item: (item.path, item.cell or -1, item.kind))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wm-notecards")
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor = subparsers.add_parser("doctor", help="Report runtime and notebook drift risks")
    doctor.add_argument("project", nargs="?", default=".")
    doctor.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface."""
    args = _build_parser().parse_args(argv)
    findings = scan_project(Path(args.project))
    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], indent=2))
    elif not findings:
        print("No canonical-runtime drift risks found.")
    else:
        for finding in findings:
            cell = f" cell {finding.cell}" if finding.cell is not None else ""
            print(f"[{finding.kind}] {finding.path}{cell}: {finding.detail}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
