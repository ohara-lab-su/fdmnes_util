#!/usr/bin/env python3
"""同梱の例 ``scripts/*.py`` を作業フォルダへコピーする。

ScriptInstaller が配布先または開発ツリーからサンプルを探す。コマンドの実行時に計算データは読み込まない。

配布コマンドは編集可能な Python スクリプトを作業フォルダにコピーする。コピー後はパッケージのインストール先を意識せず、計算ごとに編集できる。
"""

import argparse
import sysconfig
from pathlib import Path
import shutil
from typing import Optional, Sequence


class ScriptInstaller:
    """配布用の Python サンプル ``scripts/*.py`` を作業フォルダへコピーする。"""

    @staticmethod
    def install_scripts(
        directory: Path,
        overwrite: bool = False,
    ) -> tuple[list[Path], list[Path]]:
        """同梱サンプルを指定フォルダへコピーする。

        overwrite を明示した場合にだけ既存ファイルを上書きする。サンプルは通常の Python ソースとして保存する。

        Args:
            directory: 対象ディレクトリ。通常は作業ディレクトリ。
            overwrite: True の場合は既存スクリプトを置き換える。

        Returns:
            tuple[list[Path], list[Path]]: コピーしたファイルのパスと、スキップしたパス。

        Raises:
            FileNotFoundError: パッケージのサンプルが存在しない場合。
            NotADirectoryError: 保存先がディレクトリではない場合。
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
    """`fdmnes_util` 管理コマンドを実行する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        int: 正常終了時は0。
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
