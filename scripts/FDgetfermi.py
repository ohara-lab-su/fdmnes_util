#!/usr/bin/env python3
# SAE original: sae/commands/FDgetfermi.py
# ---- SAE original header (verbatim) ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# get E_fermi
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.11.16 startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""生 XAS ``<Filout>.txt`` と ``*_bav.txt`` を読み、フェルミ準位と吸収端を表示する。

接頭辞はコマンドライン、または ``*.inp`` の Filout から決める。
"""
import argparse

from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.fdmfile import Fdmfile


def main(argv=None):
    """必要なファイルを読み、計算されたエネルギーを表示する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。
    """
    parser = argparse.ArgumentParser(description="Report FDMNES energies")
    parser.add_argument("-i", "--input", help="FDMNES calculation input")
    parser.add_argument("--name", help="Output prefix overriding Filout")
    options = parser.parse_args(argv)

    if options.name:
        filout = options.name
    else:
        try:
            input_path = Fdmfile.select_input(options.input)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        input_file = FdmInp(input_path)
        filout = input_file.get_filout()

    if not filout:
        raise ValueError("Filout is missing")

    spectrum = FdmTxt(f"{filout}.txt")
    log = FdmBav(f"{filout}_bav.txt").select_reader()

    print("E_Fermi")
    print(spectrum.get_efermi())
    print(f"E_Edge ({log.get_edge()})")
    print(spectrum.get_eedge())


if __name__ == "__main__":
    main()
