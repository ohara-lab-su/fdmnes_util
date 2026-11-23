#!/usr/bin/env python3
"""同梱の例 ``scripts/*.py`` を作業フォルダへコピーする。

ScriptInstaller が配布先または開発ツリーからサンプルを探す。コマンドの実行時に計算データは読み込まない。

配布コマンドは編集可能な Python スクリプトを作業フォルダにコピーする。コピー後はパッケージのインストール先を意識せず、計算ごとに編集できる。
"""

import argparse
import ast
import shutil
import sysconfig
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from typing import Optional, Sequence


class ScriptInstaller:
    """配布用の Python サンプル ``scripts/*.py`` を作業フォルダへコピーする。"""

    @staticmethod
    def _script_sources() -> list[Path]:
        """インストール記録または開発ツリーから配布スクリプトをファイル名順に取得する。"""
        share_path = ("share", "fdmnes_util", "scripts")
        try:
            package = distribution("fdmnes-util")
        except PackageNotFoundError:
            package = None
        entries = None
        if package is not None:
            entries = package.files
        if entries is not None:
            # RECORD を使うと --user で導入した場合も配布ファイルを見つけられる。
            recorded = []
            for entry in entries:
                if entry.parts[-4:-1] == share_path and entry.suffix == ".py":
                    path = Path(package.locate_file(entry))
                    if path.is_file():
                        recorded.append(path)
            if recorded:
                return sorted(recorded, key=lambda path: path.name)

        installed = Path(sysconfig.get_path("data")).joinpath(*share_path)
        checkout = Path(__file__).resolve().parents[2] / "scripts"
        for directory in (installed, checkout):
            sources = [path for path in directory.glob("*.py") if path.is_file()]
            if sources:
                return sorted(sources, key=lambda path: path.name)
        raise FileNotFoundError("Installed example scripts were not found")

    @staticmethod
    def list_scripts() -> list[tuple[str, str]]:
        """インストール時に指定するスクリプト名と、説明の先頭行を返す。"""
        scripts = []
        for path in ScriptInstaller._script_sources():
            source = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            docstring = ast.get_docstring(source)
            summary = "説明なし"
            if docstring:
                summary = docstring.strip().splitlines()[0].replace("``", "")
            scripts.append((path.stem, summary))
        return scripts

    @staticmethod
    def install_scripts(
        directory: Path,
        overwrite: bool = False,
        *,
        name: Optional[str] = None,
    ) -> tuple[list[Path], list[Path]]:
        """同梱サンプルを指定フォルダへコピーする。

        overwrite を明示した場合にだけ既存ファイルを上書きする。サンプルは通常の Python ソースとして保存する。

        Args:
            directory: 対象ディレクトリ。通常は作業ディレクトリ。
            overwrite: True の場合は既存スクリプトを置き換える。
            name: 個別にコピーするスクリプト名。拡張子は含めない。

        Returns:
            tuple[list[Path], list[Path]]: コピーしたファイルのパスと、スキップしたパス。

        Raises:
            FileNotFoundError: 配布先または指定したスクリプトが見つからない場合。
            NotADirectoryError: 保存先がディレクトリではない場合。
        """
        destination = Path(directory)
        if not destination.is_dir():
            raise NotADirectoryError(f"Destination is not a directory: {destination}")

        source_files = ScriptInstaller._script_sources()
        if name is not None:
            source_files = [source for source in source_files if source.stem == name]
            if not source_files:
                raise FileNotFoundError(f"Unknown bundled script: {name}")

        copied = []
        skipped = []

        for source in source_files:
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
    install_parser = subcommands.add_parser("install", help="Copy or list bundled scripts")
    install_parser.add_argument(
        "resource",
        nargs="?",
        default="script",
        metavar="script|list|NAME",
        help="Copy all scripts (default), list scripts, or give a name without .py",
    )
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

    if args.resource == "list":
        try:
            scripts = ScriptInstaller.list_scripts()
        except FileNotFoundError as error:
            install_parser.error(str(error))
        for name, summary in scripts:
            print(f"{name} {summary}")
        return 0

    name = None
    if args.resource != "script":
        name = args.resource
    try:
        copied, skipped = ScriptInstaller.install_scripts(
            args.directory,
            overwrite=args.force,
            name=name,
        )
    except (FileNotFoundError, NotADirectoryError) as error:
        install_parser.error(str(error))
    for path in copied:
        print(f"Installed: {path}")
    for path in skipped:
        print(f"Skipped (already exists): {path}")
    print(f"Installed {len(copied)} script(s), skipped {len(skipped)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
