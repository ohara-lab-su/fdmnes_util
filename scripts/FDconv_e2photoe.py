#!/usr/bin/env python3
# SAE original: sae/commands/FDconv_e2photoe.py
# Copyright Kengo NAKADA; SAE class library.
# K.NAKADA, kengo.nakada@gmail.com
#
# FEconv_e2photow.py
#   *_conv.txt ---> *_conv_photoe.txt
#   EF からの相対単位を Photon Energy 単位に変換して出力するプログラム
#
# 2018.08.17
#   Python2/3 両対応
"""Convert convolution energy values to photon-energy values."""

import argparse

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy


def main(argv=None):
    """Convert the convolved spectrum and write the resulting text file.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Convert XAS energy units")
    parser.add_argument("input", nargs="?", help="FDMNES input file")
    parser.add_argument("-i", "--inp", default="read_pdb.inp")
    parser.add_argument("-t", "--text")
    parser.add_argument("-c", "--conv")
    parser.add_argument("-f", "--fermi", action="store_true")
    options = parser.parse_args(argv)

    input_name = options.inp
    if options.input is not None:
        input_name = options.input

    input_file = FdmInp(input_name)
    if input_file.get_energygpho():
        raise ValueError("Input already uses PhotonEnergy")

    if options.text:
        raw_prefix = options.text.removesuffix(".txt")
    else:
        raw_prefix = input_file.get_filout()

    if options.conv:
        convolution_prefix = options.conv.removesuffix("_conv.txt")
    else:
        convolution_prefix = raw_prefix

    spectrum = FdmTxt(f"{raw_prefix}.txt")
    convolution = FdmConv(f"{convolution_prefix}_conv.txt")

    # Energy conversion stays in the analysis class, not in this example.
    energy, intensity = AnalyzeFdmXas.photon_energy(
        convolution,
        spectrum,
        subtract_fermi=options.fermi,
        fermi_energy=spectrum.get_efermi(),
    )
    writer = FdmPhotoenergy()
    output_name = f"{convolution_prefix}_conv_photoe.txt"
    output = writer.write(energy, intensity, output_name)
    print(output)
    return output


if __name__ == "__main__":
    main()
