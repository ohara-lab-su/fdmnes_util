#!/usr/bin/env python3
"""Check the example-script distribution and installation command."""

from pathlib import Path

from fdmnes_util.cli import install_scripts, main


def test_install_to_current_directory(tmp_path, monkeypatch):
    """Copy the included examples to the current working directory."""
    monkeypatch.chdir(tmp_path)
    result = main(["install", "script"])

    assert result == 0
    assert (tmp_path / "FDclean.py").is_file()
    assert (tmp_path / "FDplot_XAS.py").is_file()
    assert (tmp_path / "fdLDOS0_specified.py").is_file()


def test_existing_script_is_not_overwritten(tmp_path):
    """Preserve a locally customized script unless force was specified."""
    filename = tmp_path / "FDclean.py"
    filename.write_text("# customized by researcher\n")

    installed, skipped = install_scripts(tmp_path)

    assert filename.read_text() == "# customized by researcher\n"
    assert filename in skipped
    assert filename not in installed


def test_force_replaces_existing_script(tmp_path):
    """Allow explicit replacement of existing script files."""
    filename = tmp_path / "FDclean.py"
    filename.write_text("# customized by researcher\n")

    installed, skipped = install_scripts(tmp_path, overwrite=True)

    assert filename in installed
    assert filename not in skipped
    assert "FdmInp" in filename.read_text()


def test_script_sources_are_self_contained(tmp_path):
    """Ensure copied examples import the library rather than another script."""
    installed, skipped = install_scripts(tmp_path)
    assert installed
    assert not skipped
    for filename in installed:
        content = filename.read_text()
        assert content.startswith("#!/usr/bin/env python3")
        assert "fdmnes_util.commands" not in content
