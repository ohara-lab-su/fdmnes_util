#!/usr/bin/env python3
# SAE source: sae/commands/FDclean.py
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDclean
# *.in ファイルを読み込んで Filout タグから名前を取得し
# Filout* ファイルを消す
#
################################################################################
#
# 2020.08.11: filout 処理でのセーフティーを導入
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.06.19 startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""``*.inp`` の Filout から計算出力を特定して削除する。

入力を省略した場合は ``fdmfile.txt`` の先頭ジョブまたは ``read_pdb.inp`` を使う。対象は生 XAS ``<Filout>.txt``、``*_bav.txt``、``*_conv.txt``、``*_sdN.txt`` など。

計算入力は残す。入力リーダーと結果管理クラスを組み合わせる例。削除対象は計算フォルダと入力の Filout で指定する。
"""

import argparse

from fdmnes_util.fdm_result_files import FdmResultFiles
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdmfile import Fdmfile


def main(argv=None):
    """`Filout` に対応する出力ファイルを削除する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。
    """
    parser = argparse.ArgumentParser(description="Remove FDMNES result files")
    parser.add_argument("-i", "--input")
    parser.add_argument("input_path", nargs="?")
    options = parser.parse_args(argv)

    input_file = FdmInp(Fdmfile.select_input(options.input_path or options.input))
    filout = input_file.get_filout()
    if not filout:
        raise ValueError("The FDMNES input file has no Filout value")

    results = FdmResultFiles(filout)
    deleted_files = results.clean()
    for path in deleted_files:
        print(f"DELETE: {path}")


if __name__ == "__main__":
    main()
