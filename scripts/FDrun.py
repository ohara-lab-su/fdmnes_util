#!/usr/bin/env python3
"""入力1件または既存の ``fdmfile.txt`` で FDMNES を起動する。"""

# 実行例（このスクリプトがあるディレクトリで実行）
# --executable を省略する場合は PATH に fdmnes が必要。
#
# 現在のディレクトリにある inp.txt を1件だけ実行する。
# python FDrun.py
#
# 手元の Cu_inp.txt を位置引数で指定する。fdmfile.txt にはこの入力1件だけを記載する。
# ./FDrun.py Cu_inp.txt
#
# cu_run/Cu.inp を指定し、cu_run を作業ディレクトリにする。
# /path/to/fdmnes は実行ファイルの実際のパスに置き換える。制限時間は300秒。
# python FDrun.py Cu.inp --directory cu_run --executable /path/to/fdmnes --timeout 300
#
# cu_run に用意した fdmfile.txt をそのまま使う。このモードでは入力名を省く。
# python FDrun.py --fdmfile --directory cu_run

import argparse

from fdmnes_util.fdm_run import FdmRun


def main(argv=None):
    """計算入力または作業フォルダのジョブ一覧を実行する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Calculation input (default: inp.txt)")
    parser.add_argument("--fdmfile", action="store_true", help="Use the existing fdmfile.txt")
    parser.add_argument("--executable", default="fdmnes")
    parser.add_argument("--directory")
    parser.add_argument("--timeout", type=float)
    options = parser.parse_args(argv)
    if options.fdmfile and options.input is not None:
        parser.error("--fdmfile cannot be combined with a calculation input")
    runner = FdmRun(options.executable)
    if options.fdmfile:
        log = runner.run_fdmfile(
            directory=options.directory,
            timeout=options.timeout,
        )
    else:
        log = runner.run(
            options.input,
            directory=options.directory,
            timeout=options.timeout,
        )
    print(log)


if __name__ == "__main__":
    main()
