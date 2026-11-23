"""入力ブロックの編集と順次実行の回帰検証。"""

from pathlib import Path
from subprocess import CompletedProcess

import pytest

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun


def test_edit_preserves_unrelated_blocks_comments_and_trailing_text(tmp_path):
    original = (
        "! Leading comment\r\n"
        "File_out ! Existing spelling\r\n"
        "  old\r\n"
        "\r\n"
        "Radius\r\n"
        "! radius comment\r\n"
        "  3\r\n"
        "Calculation\r\n"
        "  first.txt\r\n"
        "  1.0 0.2\r\n"
        "End\r\n"
        "trailing note\r\n"
    )
    source = tmp_path / "original.inp"
    source.write_bytes(original.encode())
    model = FdmInp(source, format_year=2026)
    model.set_block("Filout", "new")
    model.set_radius(8.3, (100, 7), (250, 5))
    model.set_block("Convolution")
    assert model.get_filout() == "new"
    assert model.tags["radius"] == ["8.3 100.0 7.0 250.0 5.0"]
    assert model.get_convolution()
    target = model.save(tmp_path / "new.inp")
    assert target.read_bytes().decode() == original.replace("  old", "  new").replace(
        "  3\r\n", "  8.3 100.0 7.0 250.0 5.0\r\n"
    ).replace("End\r\n", "Convolution\r\n\r\nEnd\r\n")
    assert source.read_bytes() == original.encode()
    with pytest.raises(FileExistsError):
        model.save(source)
    with pytest.raises(ValueError, match="format_year=2026"):
        FdmInp(source).set_radius(4)


def test_variable_block_replacement_requires_an_explicit_boundary():
    model = FdmInp.from_text("Calculation\na.txt\n1 0\nConvolution\nEnd\n")
    with pytest.raises(ValueError, match="Specify old_rows"):
        model.set_block("Calculation", "b.txt")
    with pytest.raises(ValueError, match="Incomplete"):
        model.set_block("Calculation", "b.txt", old_rows=3)
    model.set_block("Calculation", "b.txt", (0.5, 0.25), old_rows=2)
    model.remove_block("Convolution")
    assert model.render_input() == "Calculation\n  b.txt\n  0.5 0.25\nEnd\n"


def test_ordered_inputs_restore_original_job_list(tmp_path, monkeypatch):
    executable = tmp_path / "fdmnes"
    executable.touch()
    for job in ("b.inp", "a.inp"):
        FdmInp(None, format_year=2026).save(tmp_path / job)
    jobs = tmp_path / "fdmfile.txt"
    jobs.write_bytes(b"1\noriginal.inp\n")

    launched = []

    def native_run(args, **kwargs):
        assert Path(args[0]) == executable
        assert kwargs["cwd"] == tmp_path
        assert 0 < kwargs["timeout"] <= 30
        count, name = jobs.read_text().split()
        assert count == "1"
        launched.append(name)
        return CompletedProcess(args, 0)

    monkeypatch.setattr("fdmnes_util.fdm_run.subprocess.run", native_run)
    logs = FdmRun(executable).run_inputs(
        ["b.inp", "a.inp"],
        directory=tmp_path,
        timeout=30,
    )
    assert launched == ["b.inp", "a.inp"]
    assert len(set(logs)) == 2
    assert all(log.is_file() for log in logs)
    assert jobs.read_bytes() == b"1\noriginal.inp\n"
