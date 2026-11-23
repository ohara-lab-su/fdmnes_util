#!/usr/bin/env python3
"""配布サンプルとインストールコマンドを検証する。"""

import pytest

from fdmnes_util.cli import ScriptInstaller, install_scripts, main


@pytest.mark.parametrize("args", [["install"], ["install", "script"]])
def test_install_to_current_directory(tmp_path, monkeypatch, args):
    """同梱サンプルを現在の作業フォルダにコピーすることを検証する。"""
    monkeypatch.chdir(tmp_path)
    result = main(args)

    assert result == 0
    assert (tmp_path / "FDclean.py").is_file()
    assert (tmp_path / "FDplot_XAS.py").is_file()
    assert (tmp_path / "fdLDOS0_specified.py").is_file()
    assert {path.stem for path in tmp_path.glob("*.py")} == {
        name for name, _ in ScriptInstaller.list_scripts()
    }


def test_install_script_by_name(tmp_path, monkeypatch):
    """拡張子を除いた名前で指定した1本だけをコピーする。"""
    monkeypatch.chdir(tmp_path)

    assert main(["install", "FDplot_XAS"]) == 0
    assert [path.name for path in tmp_path.iterdir()] == ["FDplot_XAS.py"]


@pytest.mark.parametrize("args", [["install", "list"], ["install", "script", "list"]])
def test_list_script_names_and_japanese_descriptions(
    tmp_path,
    monkeypatch,
    capsys,
    args,
):
    """名前と日本語の説明を1行ずつ表示し、ファイルを作らない。"""
    monkeypatch.chdir(tmp_path)

    assert main(args) == 0
    heading, separator, *rows = capsys.readouterr().out.splitlines()
    scripts = ScriptInstaller.list_scripts()
    name_width = max(len(name) for name, _ in scripts)
    description_column = name_width + 2
    assert heading.split() == ["スクリプト名", "説明"]
    assert heading.index("説明") + len("スクリプト名") == description_column
    assert separator.split()[0] == "-" * name_width
    assert len(rows) == len(scripts)
    for row, (name, explanation) in zip(rows, scripts):
        assert row[:name_width].rstrip() == name
        assert row[name_width:description_column] == "  "
        assert row[description_column:] == explanation
        assert len(explanation) <= 32
        assert any("ぁ" <= character <= "ん" for character in explanation)
    assert ("FDrun", "入力1件または既存のジョブ一覧を実行") in scripts
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("name", ["unknown", "FDplot_XAS.py"])
def test_install_rejects_unknown_name(tmp_path, monkeypatch, capsys, name):
    """個別インストールには一覧にある名前をそのまま指定する。"""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as error:
        main(["install", name])
    assert error.value.code == 2
    assert f"Unknown bundled script: {name}" in capsys.readouterr().err
    assert not list(tmp_path.iterdir())


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
