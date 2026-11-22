"""``*.inp`` または ``fdmfile.txt`` の一覧で FDMNES を起動し、``fdmnes-*.log`` に実行ログを保存する。

FdmRun は指定順に本体へジョブを渡す。入力を明示して一時一覧を作る場合は、終了時に元の一覧を復元する。
"""
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from .fdmfile import Fdmfile


class FdmRun:
    """FDMNES の計算入力 `*.inp` とジョブ一覧 `fdmfile.txt` を使い、計算を起動し、実行ログ `fdmnes-*.log` を保存する。"""
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
            input_file: 入力ファイル。指定すると一件だけ実行する。 directory を指定した場合、相対パスの基準はそのフォルダ。
            directory: 計算フォルダ。省略時は入力の親フォルダか現在位置。
            timeout: 実行の制限時間（秒）。

        Returns:
            Path: 保存した実行ログ。

        Raises:
            RuntimeError: 計算の異常終了時。
            subprocess.TimeoutExpired: 制限時間を超えた場合。
        """
        if input_file is None:
            return self._run((), directory=directory, timeout=timeout)
        return self._run((input_file,), directory=directory, timeout=timeout)

    def run_inputs(self, input_files, *, directory, timeout=None):
        """入力の並びを一時ジョブ一覧に書き、FDMNES で指定順に実行する。

        相対パスは directory 基準。制限時間はバッチ全体に適用する。
        """
        inputs = tuple(input_files)
        if not inputs:
            raise ValueError("Provide at least one FDMNES input")
        return self._run(inputs, directory=directory, timeout=timeout)

    def _run(self, inputs, *, directory, timeout):
        """同じ計算フォルダでの FdmRun の重複起動を防ぎ、終了後に一時ジョブ一覧を片づける。"""
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
        # ジョブ一覧の一時差し替えから復元まで、同じフォルダでの起動を排他する。
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise RuntimeError(f"FDMNES run already locked: {lock}") from error

        original = None
        replace_jobs = False
        try:
            if paths or not jobs.exists():
                if not paths:
                    default = cwd / "read_pdb.inp"
                    if not default.is_file():
                        raise FileNotFoundError(default)
                    paths.append(default)
                if jobs.is_symlink():
                    raise ValueError(f"Cannot replace linked job file: {jobs}")
                if jobs.exists():
                    original = jobs.read_bytes()
                replace_jobs = True
                filenames = []
                for path in paths:
                    if path.is_relative_to(cwd):
                        path = path.relative_to(cwd)
                    filenames.append(path)
                Fdmfile.write(filenames, jobs)

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
