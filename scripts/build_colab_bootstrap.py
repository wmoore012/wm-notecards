"""Build Colab exports: embed cell + COLAB notebook from a takeover notebook."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

import nbformat
from build_zerve_notebook import (
    DEFAULT_CONFIG_FILES,
    DEFAULT_PYTHON_EXCLUDES,
    build_colab_notebook,
    build_embed_cell_source,
    collect_root_python_files,
    collect_wm_package_files,
    dedupe_paths,
    merge_file_entries,
    resolve_named_files,
    resolve_wm_notecards_root,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

DEFAULT_OUTPUT = Path("colab_helper_cell.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a Colab helper cell and COLAB notebook with embedded "
            "wm-notecards package and project files."
        ),
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--python-file", action="append", default=None)
    parser.add_argument("--config-file", action="append", default=None)
    parser.add_argument("--skip-config-files", action="store_true")
    parser.add_argument("--takeover", type=Path, default=Path("takeover.ipynb"))
    parser.add_argument("--scratch", type=Path, default=Path("takeover.ipynb"))
    parser.add_argument("--notebook-output", type=Path, default=None)
    parser.add_argument("--skip-scratch", action="store_true")
    parser.add_argument("--skip-notebook", action="store_true")
    parser.add_argument(
        "--wm-root",
        type=Path,
        default=None,
        help="wm-notecards repository root (default: inferred from script location)",
    )
    parser.add_argument(
        "--print-one-liner",
        action="store_true",
        help="Print a one-liner that executes the generated helper cell.",
    )
    return parser.parse_args()


def build_colab_bootstrap_cell(
    *,
    file_entries: Sequence[tuple[Path, str]],
    install_wm_editable: bool,
) -> str:
    return build_embed_cell_source(
        title="Embed Project Files",
        cell_tag="embedded_project_files",
        file_entries=file_entries,
        install_wm_editable=install_wm_editable,
    )


def main() -> None:
    args = parse_args()
    project_dir = Path.cwd()

    script_path = Path(__file__)
    wm_root = (
        args.wm_root.resolve() if args.wm_root else resolve_wm_notecards_root(script_path)
    )
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

    output_text = build_colab_bootstrap_cell(
        file_entries=file_entries,
        install_wm_editable=install_wm,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output_text + "\n", encoding="utf-8")

    print(f"Wrote Colab helper cell: {args.output}")
    print(f"Embedded {len(file_entries)} files from: {project_dir} + wm-notecards")

    notebook_output = args.notebook_output
    if notebook_output is None:
        notebook_output = Path(f"{args.takeover.stem}_COLAB.ipynb")

    if not args.skip_notebook:
        include_scratch = not args.skip_scratch and args.scratch.resolve().is_file()
        generated_nb = build_colab_notebook(
            takeover_path=args.takeover.resolve(),
            scratch_path=(args.scratch if include_scratch else args.takeover).resolve(),
            output_path=notebook_output.resolve(),
            file_entries=file_entries,
            install_wm_editable=install_wm,
            include_scratch=include_scratch,
        )
        notebook_output.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(generated_nb, notebook_output)
        print(
            "Wrote Colab notebook from takeover foundation: "
            f"{notebook_output} ({len(generated_nb.cells)} cells)"
        )

    if args.print_one_liner:
        print("One-liner for Colab helper cell execution:")
        print(f"exec(Path('{args.output.as_posix()}').read_text(encoding='utf-8'))")


if __name__ == "__main__":
    main()
