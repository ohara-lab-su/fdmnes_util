#!/usr/bin/env python3
"""``*.inp`` または ``fdmfile.txt`` のジョブで FDMNES を起動し、``fdmnes-*.log`` を保存する。"""
import argparse

from fdmnes_util.fdm_run import FdmRun


def main(argv=None):
    """計算入力または作業フォルダのジョブ一覧を実行する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?")
    parser.add_argument("--executable", default="fdmnes")
    parser.add_argument("--directory")
    parser.add_argument("--timeout", type=float)
    options = parser.parse_args(argv)
    log = FdmRun(options.executable).run(
        options.input,
        directory=options.directory,
        timeout=options.timeout,
    )
    print(log)


if __name__ == "__main__":
    main()
