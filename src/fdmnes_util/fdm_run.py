"""計算入力 ``inp.txt``・``*.inp`` または既存の ``fdmfile.txt`` で FDMNES を起動する。

計算入力を選んで起動する場合は、入力1件だけの ``fdmfile.txt`` を一時的に用意する。
各起動の標準出力と標準エラーは ``fdmnes-*.log`` に保存する。
"""

import re
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import monotonic

from .fdmfile import Fdmfile


class FdmRun:
    """計算入力 ``inp.txt``・``*.inp`` とジョブ一覧 ``fdmfile.txt`` を使って FDMNES を起動する。"""

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

    def run(self, input_file="inp.txt", *, directory=None, timeout=None):
        """指定した計算入力だけを実行し、ログのパスを返す。

        Args:
            input_file: 計算入力のパス。省略した場合は inp.txt。
            directory: 計算フォルダ。省略した場合は入力の親フォルダ。
            timeout: 実行の制限時間（秒）。

        Raises:
            FileNotFoundError: 計算入力が存在しない場合。
            RuntimeError: 計算が異常終了した場合。
            subprocess.TimeoutExpired: 制限時間を超えた場合。
        """
        if input_file is None:
            input_file = "inp.txt"
        return self._run((input_file,), directory=directory, timeout=timeout)[0]

    def run_fdmfile(self, *, directory=None, timeout=None):
        """既存の fdmfile.txt を使って起動し、ログのパスを返す。

        Args:
            directory: fdmfile.txt がある計算フォルダ。省略時は現在のフォルダ。
            timeout: 実行の制限時間（秒）。
        """
        return self._run((), directory=directory, timeout=timeout)[0]

    def run_inputs(self, input_files, *, directory, timeout=None):
        """入力を指定順に1件ずつ実行し、各実行のログのパスを順に返す。

        Args:
            input_files: 実行順に並べた計算入力ファイル。
            directory: 計算フォルダ。入力の相対パスはこのフォルダを基準とする。
            timeout: すべての起動を合わせた制限時間（秒）。
        """
        inputs = tuple(input_files)
        if not inputs:
            raise ValueError("Provide at least one FDMNES input")
        return self._run(inputs, directory=directory, timeout=timeout)

    def _run(self, inputs, *, directory, timeout):
        """計算フォルダを排他し、入力1件ごとの起動と既存一覧での起動を扱う。"""
        cwd = Path.cwd()
        if directory is not None:
            cwd = Path(directory).expanduser().resolve()
        paths = [(cwd / Path(item).expanduser()).resolve() for item in inputs]
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
        if paths and directory is None:
            cwd = paths[0].parent

        jobs = cwd / "fdmfile.txt"
        lock = cwd / ".fdmnes-run.lock"
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise RuntimeError(f"FDMNES run already locked: {lock}") from error

        original = None
        replace_jobs = False
        try:
            if not paths:
                self._run_validate_fdmfile(jobs)
                return [self._launch(cwd, timeout)]

            if jobs.is_symlink():
                raise ValueError(f"Cannot replace linked job file: {jobs}")
            if jobs.exists():
                original = jobs.read_bytes()

            logs = []
            started = monotonic()
            for path in paths:
                if not path.is_file():
                    raise FileNotFoundError(path)
                filename = path
                if path.is_relative_to(cwd):
                    filename = path.relative_to(cwd)
                remaining = timeout
                if timeout is not None and len(paths) > 1:
                    remaining = timeout - (monotonic() - started)
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired([str(self.executable)], timeout)
                replace_jobs = True
                Fdmfile.write([filename], jobs)
                logs.append(self._launch(cwd, remaining))
            return logs
        finally:
            # タイムアウトや異常終了でも、以前の一覧を復元してからロックを解放する。
            try:
                if replace_jobs:
                    if original is None:
                        jobs.unlink(missing_ok=True)
                    else:
                        jobs.write_bytes(original)
            finally:
                lock.rmdir()

    @staticmethod
    def _run_validate_fdmfile(jobs):
        """既存一覧の入力の存在を確認する。相対パスは一覧のフォルダが基準。"""
        if not jobs.is_file():
            raise FileNotFoundError(jobs)
        for filename in Fdmfile(jobs).filenames:
            path = jobs.parent / filename
            if path.is_file():
                continue
            # FDMNES 本体はこの条件で、指定名に .txt を付けて開き直す。
            if len(filename) > 4 and filename[-4] != ".":
                if (jobs.parent / f"{filename}.txt").is_file():
                    continue
            raise FileNotFoundError(path)

    def _launch(self, cwd, timeout):
        """計算フォルダの fdmfile.txt で本体を起動し、ログのパスを返す。"""
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
        # Fortran の STOP は、終了コードが0でもログに記録されることがある。
        with log.open(encoding="utf-8", errors="replace") as stream:
            if any(re.match(r"\s*STOP(?:\s|:|$)", line, re.I) for line in stream):
                raise RuntimeError(f"FDMNES reported STOP: {log}")
        return log
