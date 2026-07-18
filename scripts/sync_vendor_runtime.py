"""Synchronize wm-notecards into a project's vendored runtime directory."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy or verify the canonical wm_notecards package in a vendor target.",
    )
    parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="Target src/wm_notecards directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report differences without writing files.",
    )
    return parser.parse_args()


def canonical_package_root() -> Path:
    return Path(__file__).resolve().parents[1] / "src" / "wm_notecards"


def package_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.name != ".DS_Store"
    }


def diff_vendor(source: Path, target: Path) -> tuple[list[str], list[str]]:
    source_files = package_files(source)
    target_files = package_files(target) if target.is_dir() else {}
    changed = [
        relative
        for relative, source_path in source_files.items()
        if relative not in target_files
        or not filecmp.cmp(source_path, target_files[relative], shallow=False)
    ]
    stale = sorted(set(target_files) - set(source_files))
    return sorted(changed), stale


def sync_vendor(source: Path, target: Path) -> tuple[list[str], list[str]]:
    changed, stale = diff_vendor(source, target)
    for relative in changed:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    return changed, stale


def main() -> int:
    args = parse_args()
    source = canonical_package_root()
    target = args.target.expanduser().resolve()
    changed, stale = diff_vendor(source, target)

    if args.check:
        if changed or stale:
            print(f"Vendor runtime differs: {len(changed)} changed/missing, {len(stale)} stale")
            for relative in changed:
                print(f"  update {relative}")
            for relative in stale:
                print(f"  stale  {relative}")
            return 1
        print("Vendor runtime is synchronized.")
        return 0

    changed, stale = sync_vendor(source, target)
    print(f"Synchronized {len(changed)} files into {target}")
    if stale:
        print("Stale target files were preserved; remove them only after review:")
        for relative in stale:
            print(f"  {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
