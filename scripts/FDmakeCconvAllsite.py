#!/usr/bin/env python3
# SAE source: sae/commands/FDmakeCconvAllsite.py
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDmakeConvAllsite.py
#
#  allsite 計算用
#
#   -i conv.inp
#    を参照して すべてのサイトの conv を行う conv.inp と fdmfile.txt を作成する
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.06.30 startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""Generate all-site convolution input files from an existing calculation."""

import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_convolution_inputs import FdmConvolutionInputs


def main(argv=None):
    """Read Filout and create all-site convolution job files.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Prepare all-site convolutions")
    parser.add_argument("-i", "--input", default="read_pdb.inp", type=Path)
    options = parser.parse_args(argv)

    input_path = options.input
    if not input_path.is_file():
        input_path = Path("conv.inp")
    calculation = FdmInp(input_path)
    filout = calculation.get_filout()
    if not filout:
        raise ValueError("Filout is missing")

    writer = FdmConvolutionInputs()
    generated_paths = writer.write(filout)
    for path in generated_paths:
        print(path)


if __name__ == "__main__":
    main()
