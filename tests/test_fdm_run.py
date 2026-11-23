"""FDMNES のジョブファイル管理とログ保存を検証する。"""

import os
import subprocess

import pytest

from fdmnes_util.fdm_run import FdmRun
from fdmnes_util.fdmfile import Fdmfile


@pytest.mark.skipif(os.name == "nt", reason="Uses a POSIX test executable")
def test_run_restores_job_file_on_success_and_stop(tmp_path):
    executable = tmp_path / "fake-fdmnes"
    executable.write_text("#!/bin/sh\ncat fdmfile.txt\n")
    executable.chmod(0o700)
    (tmp_path / "model.inp").write_text("End\n")
    (tmp_path / "inp.txt").write_text("End\n")
    (tmp_path / "original.inp").write_text("End\n")
    job_file = tmp_path / "fdmfile.txt"
    Fdmfile.write(["original.inp"], job_file)
    original = job_file.read_bytes()

    runner = FdmRun(executable)
    log = runner.run("model.inp", directory=tmp_path)
    assert "model.inp" in log.read_text()
    assert job_file.read_bytes() == original
    default_log = runner.run(directory=tmp_path)
    assert default_log.read_text().split() == ["1", "inp.txt"]
    assert job_file.read_bytes() == original
    assert runner.run_fdmfile(directory=tmp_path).read_bytes() == original
    assert job_file.read_bytes() == original

    executable.write_text("#!/bin/sh\nprintf 'STOP invalid input\\n'\n")
    with pytest.raises(RuntimeError, match="reported STOP"):
        runner.run("model.inp", directory=tmp_path)
    assert job_file.read_bytes() == original
    assert not (tmp_path / ".fdmnes-run.lock").exists()


@pytest.mark.skipif(os.name == "nt", reason="Uses a POSIX test executable")
@pytest.mark.parametrize("echo", [False, True])
def test_timeout_removes_generated_job_file(tmp_path, echo):
    executable = tmp_path / "fake-fdmnes"
    executable.write_text("#!/bin/sh\nexec sleep 10\n")
    executable.chmod(0o700)
    (tmp_path / "inp.txt").write_text("End\n")

    with pytest.raises(subprocess.TimeoutExpired):
        FdmRun(executable, echo=echo).run(directory=tmp_path, timeout=0.1)
    assert not (tmp_path / "fdmfile.txt").exists()
    assert not (tmp_path / ".fdmnes-run.lock").exists()
    assert len(tuple(tmp_path.glob("fdmnes-*.log"))) == 1


@pytest.mark.skipif(os.name == "nt", reason="Uses a POSIX test executable")
@pytest.mark.parametrize("existing_list", [False, True])
def test_run_echoes_stdout_and_does_not_create_output_directory(
    tmp_path,
    monkeypatch,
    existing_list,
):
    """計算終了を待たずに標準出力を表示し、同じ内容をログに書く。"""
    executable = tmp_path / "fdmnes"
    executable.write_text(
        "#!/bin/sh\n"
        "test ! -d Sim || exit 2\n"
        "printf 'first line\\n'\n"
        "while [ ! -f seen ]; do sleep 0.01; done\n"
        "printf 'second line\\n'\n",
        encoding="utf-8",
    )
    executable.chmod(0o700)
    (tmp_path / "Cu_inp.txt").write_text(
        "Filout\nSim/Test_stand/Cu\nEnd\n",
        encoding="utf-8",
    )

    class Screen:
        def __init__(self):
            self.lines = []

        def write(self, line):
            self.lines.append(line)
            (tmp_path / "seen").touch()

        def flush(self):
            pass

    screen = Screen()
    monkeypatch.setattr("fdmnes_util.fdm_run.sys.stdout", screen)
    runner = FdmRun(executable, echo=True)
    if existing_list:
        Fdmfile.write(["Cu_inp.txt"], tmp_path / "fdmfile.txt")
        log = runner.run_fdmfile(directory=tmp_path, timeout=3)
    else:
        log = runner.run("Cu_inp.txt", directory=tmp_path, timeout=3)

    assert screen.lines == ["first line\n", "second line\n"]
    assert log.read_bytes() == b"first line\nsecond line\n"
    assert not (tmp_path / "Sim").exists()


def test_missing_inputs_stop_before_launch(tmp_path):
    executable = tmp_path / "fdmnes"
    executable.touch()
    job_file = tmp_path / "fdmfile.txt"
    Fdmfile.write(["absent.inp"], job_file)
    original = job_file.read_bytes()
    runner = FdmRun(executable)
    (tmp_path / "first.inp").write_text("End\n")

    with pytest.raises(FileNotFoundError, match="inp.txt"):
        runner.run(directory=tmp_path)
    with pytest.raises(FileNotFoundError, match="missing.inp"):
        runner.run("missing.inp", directory=tmp_path)
    with pytest.raises(FileNotFoundError, match="second.inp"):
        runner.run_inputs(["first.inp", "second.inp"], directory=tmp_path)
    with pytest.raises(FileNotFoundError, match="absent.inp"):
        runner.run_fdmfile(directory=tmp_path)

    assert job_file.read_bytes() == original
    assert not list(tmp_path.glob("fdmnes-*.log"))
    assert not (tmp_path / ".fdmnes-run.lock").exists()
