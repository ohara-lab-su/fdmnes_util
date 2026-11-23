"""計算入力 ``inp.txt``・``*.inp`` または既存の ``fdmfile.txt`` で FDMNES を起動する。

計算フォルダに入力1件を記載した ``fdmfile.txt`` を書き、実行後も残す。
本体には呼び出し元の標準入出力を引き継がせる。
"""

import shutil
import subprocess
from pathlib import Path
from time import monotonic

from .fdmfile import Fdmfile


class FdmRun:
    """計算入力 ``inp.txt``・``*.inp`` とジョブ一覧 ``fdmfile.txt`` を使って FDMNES を起動する。"""

    def __init__(self, executable="fdmnes", *, echo=True):
        """実行ファイルを指定する。

        Args:
            executable: 実行ファイルのパスまたは PATH 上のコマンド名。
            echo: 従来の呼び出しとの互換用。標準出力は値にかかわらず引き継ぐ。
        """
        candidate = Path(executable).expanduser()
        if candidate.is_file():
            self.executable = candidate.resolve()
        else:
            found = shutil.which(str(candidate))
            if found is None:
                raise FileNotFoundError(f"FDMNES executable not found: {executable}")
            self.executable = Path(found).resolve()

    def run(self, input_file=None, *, directory=None, timeout=None):
        """指定した入力1件または既存の一覧で実行し、終了結果を返す。

        Args:
            input_file: 計算入力のパス。省略時は既存の fdmfile.txt を使う。
            directory: 計算フォルダ。省略した場合は呼び出し時のカレントディレクトリ。
            timeout: 実行の制限時間（秒）。

        Raises:
            FileNotFoundError: 必要なジョブ一覧または計算入力が存在しない場合。
            RuntimeError: 計算が異常終了した場合。
            subprocess.TimeoutExpired: 制限時間を超えた場合。
        """
        if input_file is None:
            return self.run_fdmfile(directory=directory, timeout=timeout)
        return self._run((input_file,), directory=directory, timeout=timeout)[0]

    def run_fdmfile(self, *, directory=None, timeout=None):
        """既存の fdmfile.txt を使って起動し、終了結果を返す。

        Args:
            directory: fdmfile.txt がある計算フォルダ。省略時は現在のフォルダ。
            timeout: 実行の制限時間（秒）。
        """
        return self._run((), directory=directory, timeout=timeout)[0]

    def run_inputs(self, input_files, *, directory, timeout=None):
        """入力を指定順に1件ずつ実行し、各実行の終了結果を順に返す。

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
        """作業フォルダに一覧を用意し、本体を入力ごとに起動する。"""
        cwd = Path.cwd()
        if directory is not None:
            cwd = Path(directory).expanduser().resolve()
        if not inputs:
            self._run_validate_fdmfile(cwd / "fdmfile.txt")
            return [self._launch(cwd, timeout)]

        paths = [(cwd / Path(item).expanduser()).resolve() for item in inputs]
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(path)
        jobs = cwd / "fdmfile.txt"
        if jobs.is_symlink():
            raise ValueError(f"Cannot replace linked job file: {jobs}")

        results = []
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
            Fdmfile.write([filename], jobs)
            results.append(self._launch(cwd, remaining))
        return results

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
        """標準入出力を引き継いで、計算フォルダで FDMNES を起動する。"""
        result = subprocess.run(
            [str(self.executable)],
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"FDMNES exited with {result.returncode}")
        return result
