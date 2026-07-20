"""Build a portable notebook with embedded wm-notecards package source."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING

import nbformat
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_TAKEOVER = Path("takeover.ipynb")
DEFAULT_SCRATCH = Path("takeover.ipynb")
DEFAULT_OUTPUT = Path("built_portable.ipynb")
DEFAULT_CONFIG_FILES = ("pyproject.toml",)
DEFAULT_PYTHON_EXCLUDES = {
    "build_colab_bootstrap.py",
    "build_zerve_notebook.py",
    "colab_bootstrap_cell.py",
    "colab_helper_cell.py",
}
CELL_ID_RE = re.compile(
    r"(?:<!--\s*CELL:\s*([^\s]+)\s*-->)|(?:#\s*CELL:\s*([^\s]+))",
)

# Colab / ephemeral runtimes: extract the wm-notecards *repo* here (pyproject.toml +
# src/wm_notecards/...). This name MUST NOT be a top-level folder literally called
# ``wm_notecards`` at the notebook cwd: extracting to ``./wm_notecards/`` makes Python
# treat that directory as the ``wm_notecards`` package (PEP 420 namespace / partial
# shadowing) so ``from wm_notecards import WMTheme`` can fail before or despite
# ``pip install -e``. Vendor path avoids shadowing; see ``build_embed_cell_source``.
WM_COLAB_VENDOR_DIR = "_vendor/wm_notecards_pkg"


def resolve_wm_notecards_root(script_path: Path) -> Path:
    """Locate wm-notecards repo root (script in scripts/ or project-local copy)."""
    here = script_path.resolve().parent
    candidate = here.parent
    if (candidate / "src" / "wm_notecards").is_dir():
        return candidate
    sibling = here.parent / "wm-notecards"
    if (sibling / "src" / "wm_notecards").is_dir():
        return sibling.resolve()
    msg = (
        "Could not find wm-notecards (expected src/wm_notecards). "
        f"Tried {candidate} and {sibling}"
    )
    raise FileNotFoundError(msg)


def collect_wm_package_files(wm_root: Path) -> list[tuple[Path, str]]:
    """Package files to embed for Colab (under ``WM_COLAB_VENDOR_DIR``)."""
    root = wm_root.resolve()
    prefix = WM_COLAB_VENDOR_DIR
    pkg = root / "src" / "wm_notecards"
    if not pkg.is_dir():
        raise FileNotFoundError(f"Missing package directory: {pkg}")
    py_paths = sorted(pkg.rglob("*.py"))
    entries: list[tuple[Path, str]] = [
        (p, f"{prefix}/{p.relative_to(root).as_posix()}") for p in py_paths
    ]
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        raise FileNotFoundError(f"Missing {pyproject}")
    entries.append((pyproject, f"{prefix}/pyproject.toml"))
    entries.sort(key=lambda item: item[1])
    for _path, key in entries:
        if not key.startswith(f"{prefix}/"):
            msg = f"Invalid embed key (must start with {prefix}/): {key}"
            raise ValueError(msg)
    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a portable notebook from takeover, embedded project files, "
            "wm-notecards package source, and optional scratch appendix cells."
        ),
    )
    parser.add_argument("--takeover", type=Path, default=DEFAULT_TAKEOVER)
    parser.add_argument("--scratch", type=Path, default=DEFAULT_SCRATCH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--wm-root",
        type=Path,
        default=None,
        help="wm-notecards repository root (default: inferred from script location)",
    )
    parser.add_argument("--python-file", action="append", default=None)
    parser.add_argument("--config-file", action="append", default=None)
    parser.add_argument("--skip-scratch", action="store_true")
    parser.add_argument("--skip-config-files", action="store_true")
    return parser.parse_args()


def read_notebook(path: Path) -> NotebookNode:
    return nbformat.read(path, as_version=4)


def clear_cell_state(cell: NotebookNode) -> NotebookNode:
    clone = deepcopy(cell)
    if clone.cell_type == "code":
        clone.execution_count = None
        clone.outputs = []
    return clone


def cell_identity(cell: NotebookNode) -> str:
    match = CELL_ID_RE.search(cell.source)
    if match:
        return next(group for group in match.groups() if group)

    digest = hashlib.sha1(cell.source.encode("utf-8")).hexdigest()[:12]
    return f"{cell.cell_type}:{digest}"


def collect_root_python_files(project_dir: Path, *, exclude: set[str]) -> list[Path]:
    paths = list(project_dir.glob("*.py")) + list(project_dir.glob("lib/*.py"))
    return sorted(path for path in paths if path.is_file() and path.name not in exclude)


def dedupe_paths(paths: Sequence[Path]) -> list[Path]:
    seen: set[Path] = set()
    deduped: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        deduped.append(path)
    return deduped


def resolve_named_files(
    project_dir: Path,
    names: Sequence[str] | None,
    *,
    default_names: Sequence[str] | None = None,
) -> list[Path]:
    chosen = list(names) if names is not None else list(default_names or [])
    resolved: list[Path] = []

    for name in chosen:
        path = project_dir / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing file to embed: {path}")
        resolved.append(path)

    return resolved


def sanitize_embedded_python_source(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    idx = 0

    while idx < len(lines):
        line = lines[idx]

        if line in ("# NOTE TO AI EDITORS:", "# NOTE TO FUTURE AI EDITORS:"):
            idx += 1
            while idx < len(lines) and lines[idx].startswith("#"):
                idx += 1
            while idx < len(lines) and not lines[idx].strip():
                idx += 1
            continue

        if line.strip() == 'WM_NOTEBOOK_LANGUAGE_GUIDE = """':
            kept.append(
                'WM_NOTEBOOK_LANGUAGE_GUIDE = "Source-only guide omitted from embedded runtime files."'
            )
            idx += 1
            found_guide_end = False
            while idx < len(lines):
                if lines[idx].lstrip().startswith('"""'):
                    found_guide_end = True
                    idx += 1
                    break
                idx += 1
            if not found_guide_end:
                return text if text.endswith("\n") else text + "\n"
            while idx < len(lines) and not lines[idx].strip():
                idx += 1
            continue

        kept.append(line)
        idx += 1

    collapsed: list[str] = []
    for line in kept:
        if line or not collapsed or collapsed[-1]:
            collapsed.append(line)

    return "\n".join(collapsed).strip("\n") + "\n"


def merge_file_entries(
    project_dir: Path,
    *,
    local_py: Sequence[Path],
    config_files: Sequence[Path],
    wm_entries: Sequence[tuple[Path, str]],
) -> list[tuple[Path, str]]:
    pd = project_dir.resolve()
    out: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for path in local_py:
        key = str(path.resolve().relative_to(pd))
        if key not in seen:
            seen.add(key)
            out.append((path.resolve(), key))
    for path in config_files:
        key = str(path.resolve().relative_to(pd))
        if key not in seen:
            seen.add(key)
            out.append((path.resolve(), key))
    for path, key in wm_entries:
        if key not in seen:
            seen.add(key)
            out.append((path.resolve(), key))
    return out


def build_embed_cell_source(
    *,
    title: str,
    cell_tag: str,
    file_entries: Sequence[tuple[Path, str]],
    install_wm_editable: bool = False,
) -> str:
    embedded: dict[str, str] = {}
    for path, key in file_entries:
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            raw = sanitize_embedded_python_source(raw)
        embedded[key] = raw

    payload = json.dumps(embedded, indent=2, ensure_ascii=True, sort_keys=True)
    payload_b64 = base64.b64encode(gzip.compress(payload.encode("utf-8"))).decode("ascii")
    payload_chunks = [payload_b64[idx : idx + 88] for idx in range(0, len(payload_b64), 88)]
    payload_literal = "\n".join(f'    "{chunk}"' for chunk in payload_chunks)

    lines: list[str] = [
        f'#@title {title} {{ display-mode: "form" }}',
        f"# CELL: {cell_tag}",
        "# Run this helper cell once before imports in ephemeral runtimes.",
        "import base64",
        "import gzip",
        "import json",
        "import os",
        "import importlib.util",
        "from pathlib import Path",
        "",
        "EMBEDDED_FILES_B64 = (",
        payload_literal,
        ")",
        "EMBEDDED_FILES = json.loads(",
        "    gzip.decompress(base64.b64decode(EMBEDDED_FILES_B64.encode('ascii'))).decode(",
        "        'utf-8'",
        "    )",
        ")",
        "",
        "for relative_path, text in EMBEDDED_FILES.items():",
        "    file_path = Path(relative_path)",
        "    file_path.parent.mkdir(parents=True, exist_ok=True)",
        '    file_path.write_text(text, encoding="utf-8")',
        "",
        'os.environ["WM_NOTEBOOK_ROOT"] = str(Path.cwd())',
        'Path(".wm_notebook_root").write_text(str(Path.cwd()), encoding="utf-8")',
        "",
        'print(f"Wrote {len(EMBEDDED_FILES)} embedded files into {Path.cwd()}")',
        'print("Files:", ", ".join(sorted(EMBEDDED_FILES)))',
    ]

    if install_wm_editable:
        vendor = WM_COLAB_VENDOR_DIR
        lines.extend(
            [
                "",
                f"# Editable install from {vendor}/ only when wm_notecards is not already importable.",
                "# Local .venv: skip pip (avoids CalledProcessError when pip disagrees with uv).",
                "# Ephemeral Colab: find_spec is None until after install.",
                "import subprocess as _sp",
                "import sys as _sys",
                f"_wm_repo = Path({vendor!r})",
                "if _wm_repo.is_dir():",
                "    if importlib.util.find_spec('wm_notecards') is None:",
                "        _sp.run(",
                "            [_sys.executable, '-m', 'pip', 'install', '-e', str(_wm_repo), '--quiet'],",
                "            check=True,",
                "        )",
                "        print(f'Installed wm-notecards from {_wm_repo.resolve()}')",
                "        _wm_src = _wm_repo / 'src'",
                "        if _wm_src.is_dir():",
                "            _r = str(_wm_src.resolve())",
                "            if _r not in _sys.path:",
                "                _sys.path.insert(0, _r)",
                "    else:",
                "        print(",
                "            'wm_notecards already importable — skipping pip install -e '",
                "            '(use local venv / setup_project.sh; Colab skips after first run).'",
                "        )",
            ]
        )

    return "\n".join(lines)


def build_embed_cell(
    *,
    title: str,
    cell_tag: str,
    file_entries: Sequence[tuple[Path, str]],
    install_wm_editable: bool = False,
) -> NotebookNode | None:
    if not file_entries:
        return None
    source = build_embed_cell_source(
        title=title,
        cell_tag=cell_tag,
        file_entries=file_entries,
        install_wm_editable=install_wm_editable,
    )
    cell = new_code_cell(source=source)
    cell.metadata["collapsed"] = True
    cell.metadata["jupyter"] = {"source_hidden": True}
    return cell


def build_scratch_appendix_cell(_: str) -> NotebookNode:
    return new_markdown_cell(
        "\n".join(
            [
                "<!-- CELL: generated_scratch_appendix -->",
                "## Appendix: exploratory notebook-only cells",
                "These cells appear only in the scratch notebook and are not already in takeover.",
            ],
        )
    )


def build_notebook(
    *,
    takeover_path: Path,
    scratch_path: Path,
    output_path: Path,
    file_entries: Sequence[tuple[Path, str]],
    install_wm_editable: bool,
    include_scratch: bool,
) -> NotebookNode:
    _ = output_path
    takeover_nb = read_notebook(takeover_path)
    scratch_nb = read_notebook(scratch_path)

    cleaned_takeover = [clear_cell_state(cell) for cell in takeover_nb.cells]
    generated_cells: list[NotebookNode] = []

    helper_cell = build_embed_cell(
        title="Embed Project Files",
        cell_tag="embedded_project_files",
        file_entries=file_entries,
        install_wm_editable=install_wm_editable,
    )
    if helper_cell is not None:
        generated_cells.append(helper_cell)

    generated_cells.extend(cleaned_takeover)

    if include_scratch:
        takeover_ids = {cell_identity(cell) for cell in takeover_nb.cells}
        scratch_unique = [
            clear_cell_state(cell)
            for cell in scratch_nb.cells
            if cell_identity(cell) not in takeover_ids
        ]
        if scratch_unique:
            generated_cells.append(build_scratch_appendix_cell(scratch_path.name))
            generated_cells.extend(scratch_unique)

    generated_nb = new_notebook(
        cells=generated_cells,
        metadata=deepcopy(takeover_nb.metadata),
    )
    generated_nb.nbformat = takeover_nb.nbformat
    generated_nb.nbformat_minor = takeover_nb.nbformat_minor
    return generated_nb


def build_colab_notebook(
    *,
    takeover_path: Path,
    scratch_path: Path,
    output_path: Path,
    file_entries: Sequence[tuple[Path, str]],
    install_wm_editable: bool,
    include_scratch: bool,
) -> NotebookNode:
    """Same as build_notebook; named for Colab bootstrap imports."""
    return build_notebook(
        takeover_path=takeover_path,
        scratch_path=scratch_path,
        output_path=output_path,
        file_entries=file_entries,
        install_wm_editable=install_wm_editable,
        include_scratch=include_scratch,
    )


def main() -> None:
    args = parse_args()
    project_dir = Path.cwd()
    script_path = Path(__file__)
    wm_root = args.wm_root.resolve() if args.wm_root else resolve_wm_notecards_root(script_path)
    wm_entries = collect_wm_package_files(wm_root)

    if args.python_file is None:
        python_files = collect_root_python_files(
            project_dir,
            exclude=DEFAULT_PYTHON_EXCLUDES,
        )
    else:
        python_files = resolve_named_files(project_dir, args.python_file)
    python_files = dedupe_paths(python_files)

    config_files = (
        []
        if args.skip_config_files
        else resolve_named_files(
            project_dir,
            args.config_file,
            default_names=DEFAULT_CONFIG_FILES if args.config_file is None else None,
        )
    )

    file_entries = merge_file_entries(
        project_dir,
        local_py=python_files,
        config_files=config_files,
        wm_entries=wm_entries,
    )
    install_wm = bool(wm_entries)

    include_scratch = not args.skip_scratch and args.scratch.resolve().is_file()
    if not include_scratch and not args.skip_scratch:
        print(f"Scratch notebook not found, skipping appendix: {args.scratch}")

    generated_nb = build_notebook(
        takeover_path=args.takeover.resolve(),
        scratch_path=(args.scratch if include_scratch else args.takeover).resolve(),
        output_path=args.output.resolve(),
        file_entries=file_entries,
        install_wm_editable=install_wm,
        include_scratch=include_scratch,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(generated_nb, args.output)
    print(f"Wrote notebook: {args.output}")


if __name__ == "__main__":
    main()
