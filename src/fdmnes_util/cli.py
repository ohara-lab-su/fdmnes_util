#!/usr/bin/env python3
"""Manage editable example scripts distributed with fdmnes_util.

The installed command copies complete Python examples into a researcher's
working directory. After copying, each script is independent of the package's
installation location and can be edited to suit individual experiments.
"""

import argparse
import sysconfig
from pathlib import Path
import shutil
from typing import Optional, Sequence


class ScriptInstaller:
    """配布された編集用サンプルを作業ディレクトリに展開する。"""

    @staticmethod
    def install_scripts(
        directory: Path,
        overwrite: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """Copy packaged example scripts to a user-selected directory.

        Existing files are preserved unless ``overwrite`` is explicitly enabled.
        The examples are ordinary Python source files, not console entry points.

        Args:
            directory: Destination directory
            usually the current directory.
            overwrite: Replace existing script files when set to True.

        Returns:
            tuple[list[Path], list[Path]]: Copied paths and skipped paths.

        Raises:
            FileNotFoundError: When the package does not contain its examples.
            NotADirectoryError: When the destination is not a directory.
        """
        destination = Path(directory)
        if not destination.is_dir():
            raise NotADirectoryError(f"Destination is not a directory: {destination}")

        # The scripts are installed through pyproject.toml data-files.
        # They remain editable examples, not Python entry points.
        data_directory = Path(sysconfig.get_path("data"))
        scripts_resource = data_directory / "share" / "fdmnes_util" / "scripts"

        if not scripts_resource.is_dir():
            # A source checkout is also supported during development.
            project_scripts = Path(__file__).resolve().parents[2] / "scripts"
            if not project_scripts.is_dir():
                raise FileNotFoundError("Installed example scripts were not found")
            scripts_resource = project_scripts

        copied = []
        skipped = []

        # Sort by filename so installation order is predictable on all platforms.
        source_files = sorted(scripts_resource.iterdir(), key=lambda item: item.name)
        for source in source_files:
            if not source.is_file():
                continue
            if source.suffix != ".py":
                continue

            target = destination / source.name
            if target.exists() and not overwrite:
                skipped.append(target)
                continue

            shutil.copy2(source, target)
            copied.append(target)

        return copied, skipped


install_scripts = ScriptInstaller.install_scripts


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the ``fdmnes_util`` management command.

    Args:
        argv: Optional command arguments, excluding the executable name.

    Returns:
        int: Zero on successful command execution.
    """
    parser = argparse.ArgumentParser(
        prog="fdmnes_util",
        description="FDMNES Python library example-script installer",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    install_parser = subcommands.add_parser("install", help="Install package resources")
    install_parser.add_argument("resource", choices=["script"])
    install_parser.add_argument(
        "--directory",
        "-d",
        type=Path,
        default=Path.cwd(),
        help="Destination directory (default: current directory)",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files with the bundled examples",
    )
    args = parser.parse_args(argv)

    if args.command == "install":
        if args.resource != "script":
            parser.error("Unsupported install target")

        copied, skipped = ScriptInstaller.install_scripts(
            args.directory,
            overwrite=args.force,
        )
        for path in copied:
            print(f"Installed: {path}")
        for path in skipped:
            print(f"Skipped (already exists): {path}")
        print(f"Installed {len(copied)} script(s), skipped {len(skipped)}.")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
