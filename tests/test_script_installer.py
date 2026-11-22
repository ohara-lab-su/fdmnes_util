#!/usr/bin/env python3
"""配布サンプルとインストールコマンドを検証する。"""

from pathlib import Path

from fdmnes_util.cli import install_scripts, main


def test_install_to_current_directory(tmp_path, monkeypatch):
    """同梱サンプルを現在の作業フォルダにコピーすることを検証する。"""
    monkeypatch.chdir(tmp_path)
    result = main(["install", "script"])

    assert result == 0
    assert (tmp_path / "FDclean.py").is_file()
    assert (tmp_path / "FDplot_XAS.py").is_file()
    assert (tmp_path / "fdLDOS0_specified.py").is_file()


def test_existing_script_is_not_overwritten(tmp_path):
    """強制指定がなければカスタマイズ済みのサンプルを保持することを検証する。"""
    filename = tmp_path / "FDclean.py"
    filename.write_text("# customized by researcher\n")

    installed, skipped = install_scripts(tmp_path)

    assert filename.read_text() == "# customized by researcher\n"
    assert filename in skipped
    assert filename not in installed


def test_force_replaces_existing_script(tmp_path):
    """明示指定で既存のサンプルを置き換えられることを検証する。"""
    filename = tmp_path / "FDclean.py"
    filename.write_text("# customized by researcher\n")

    installed, skipped = install_scripts(tmp_path, overwrite=True)

    assert filename in installed
    assert filename not in skipped
    assert "FdmInp" in filename.read_text()


def test_script_sources_are_self_contained(tmp_path):
    """コピーしたサンプルが別のスクリプトではなくライブラリを読み込むことを検証する。"""
    installed, skipped = install_scripts(tmp_path)
    assert installed
    assert not skipped
    for filename in installed:
        content = filename.read_text()
        assert content.startswith("#!/usr/bin/env python3")
        assert "fdmnes_util.commands" not in content
