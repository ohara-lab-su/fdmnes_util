"""FDMNES を計算フォルダで実行する。"""

import re
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from .fdmfile import Fdmfile


class FdmRun:
    """FDMNES の起動、ジョブ一覧の設定、ログの保存を担当する。"""

    def __init__(self, executable="fdmnes"):
        """実行ファイルのパス、または PATH 上のコマンド名を指定する。"""
        candidate = Path(executable).expanduser()
        if candidate.is_file():
            self.executable = candidate.resolve()
        else:
            found = shutil.which(str(candidate))
            if found is None:
                raise FileNotFoundError(f"FDMNES executable not found: {executable}")
            self.executable = Path(found).resolve()

    def run(self, input_file=None, *, directory=None, timeout=None):
        """一つの入力、または計算フォルダにあるジョブ一覧を実行する。

        Args:
            input_file: 入力ファイル。指定すると一件だけ実行する。
                directory を指定した場合、相対パスの基準はそのフォルダ。
            directory: 計算フォルダ。省略時は入力の親フォルダか現在位置。
            timeout: 実行の制限時間（秒）。

        Returns:
            Path: 保存した実行ログ。

        Raises:
            RuntimeError: 計算の異常終了時。
            subprocess.TimeoutExpired: 制限時間を超えた場合。
        """
        cwd = Path.cwd()
        if directory is not None:
            cwd = Path(directory).expanduser().resolve()
        path = None
        if input_file is not None:
            path = (cwd / Path(input_file).expanduser()).resolve()
            if not path.is_file():
                raise FileNotFoundError(path)
            if directory is None:
                cwd = path.parent

        jobs = cwd / "fdmfile.txt"
        lock = cwd / ".fdmnes-run.lock"
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise RuntimeError(f"FDMNES run already locked: {lock}") from error

        original = None
        replace_jobs = False
        try:
            if path is not None or not jobs.exists():
                if path is None:
                    path = cwd / "read_pdb.inp"
                    if not path.is_file():
                        raise FileNotFoundError(path)
                if jobs.is_symlink():
                    raise ValueError(f"Cannot replace linked job file: {jobs}")
                if jobs.exists():
                    original = jobs.read_bytes()
                replace_jobs = True
                job = path
                if path.is_relative_to(cwd):
                    job = path.relative_to(cwd)
                Fdmfile.write([job], jobs)

            with NamedTemporaryFile(
                mode="wb",
                dir=cwd,
                prefix="fdmnes-",
                suffix=".log",
                delete=False,
            ) as stream:
                log = Path(stream.name)
                result = subprocess.run(
                    [str(self.executable)],
                    cwd=cwd,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    timeout=timeout,
                    check=False,
                )
            if result.returncode != 0:
                raise RuntimeError(f"FDMNES exited with {result.returncode}: {log}")
            with log.open(encoding="utf-8", errors="replace") as stream:
                if any(re.match(r"\s*STOP(?:\s|:|$)", line, re.I) for line in stream):
                    raise RuntimeError(f"FDMNES reported STOP: {log}")
            return log
        finally:
            try:
                if replace_jobs:
                    if original is None:
                        jobs.unlink(missing_ok=True)
                    else:
                        jobs.write_bytes(original)
            finally:
                lock.rmdir()
