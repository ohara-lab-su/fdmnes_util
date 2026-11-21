#!/usr/bin/env python3
"""Convert convolution energy values to photon-energy values."""

import argparse

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.read_fdm_conv import ReadFdmConv
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.read_fdm_txt import ReadFdmTxt
from fdmnes_util.write_fdm_photoenergy import WriteFdmPhotoenergy


def main(argv=None):
    """Convert the convolved spectrum and write the resulting text file.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Convert XAS energy units")
    parser.add_argument("-i", "--inp", default="read_pdb.inp")
    parser.add_argument("-t", "--text")
    parser.add_argument("-c", "--conv")
    parser.add_argument("-f", "--fermi", action="store_true")
    options = parser.parse_args(argv)

    input_file = ReadFdmInp(options.inp)
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

    spectrum = ReadFdmTxt(f"{raw_prefix}.txt")
    convolution = ReadFdmConv(f"{convolution_prefix}_conv.txt")

    # Energy conversion stays in the analysis class, not in this example.
    energy, intensity = AnalyzeFdmXas.photon_energy(
        convolution,
        spectrum,
        subtract_fermi=options.fermi,
        fermi_energy=spectrum.get_efermi(),
    )
    writer = WriteFdmPhotoenergy()
    output_name = f"{convolution_prefix}_conv_photoe.txt"
    output = writer.write(energy, intensity, output_name)
    print(output)


if __name__ == "__main__":
    main()
