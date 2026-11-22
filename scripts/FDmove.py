#!/usr/bin/env python3
# SAE source: sae/commands/FDmove.py
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDmove
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.06.19 startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""``*.inp`` の Filout で特定した ``<Filout>.txt``、``*_bav.txt``、``*_conv.txt``、``*_sdN.txt`` などを移動する。

出力の接頭辞を変更するか、元の名前で別フォルダへ移す。
"""
import argparse

from fdmnes_util.fdm_result_files import FdmResultFiles
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdmfile import Fdmfile


def main(argv=None):
    """指定された Filout 接頭辞に属するファイルを移動する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。
    """
    parser = argparse.ArgumentParser(description="Rename or archive FDMNES results")
    parser.add_argument("-i", "--input", help="Input providing the source Filout")
    parser.add_argument("-d", "--destination", help="Archive directory")
    parser.add_argument("prefixes", nargs="*", metavar="PREFIX")
    options = parser.parse_args(argv)

    if len(options.prefixes) > 2 or (options.prefixes and options.destination):
        parser.error("Specify one or two prefixes, or a destination directory")
    if not options.prefixes and options.destination is None:
        parser.error("A destination prefix or directory is required")

    if len(options.prefixes) == 2:
        filout = options.prefixes[0]
    else:
        input_file = FdmInp(Fdmfile.select_input(options.input))
        filout = input_file.get_filout()

    result_files = FdmResultFiles(filout)
    if options.prefixes:
        moved_paths = result_files.rename(options.prefixes[-1])
    else:
        moved_paths = result_files.move(options.destination)
    for path in moved_paths:
        print(f"MOVE: {path}")


if __name__ == "__main__":
    main()
