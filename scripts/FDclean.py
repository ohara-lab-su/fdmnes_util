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
"""Remove the generated FDMNES files belonging to the selected calculation.

The input file is preserved. This script illustrates how to combine the
input-file reader and the result-file manager. Modify the parameters to suit
your calculation directory before using it in a research workflow.
"""

import argparse

from fdmnes_util.fdm_result_files import FdmResultFiles
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdmfile import Fdmfile


def main(argv=None):
    """Remove the output files corresponding to ``Filout``.

    Args:
        argv: Optional command-line argument sequence.
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
