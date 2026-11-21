#!/usr/bin/env python3
"""Generate all-site convolution input files from an existing calculation."""

import argparse

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_convolution_inputs import FdmConvolutionInputs


def main(argv=None):
    """Read Filout and create all-site convolution job files.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Prepare all-site convolutions")
    parser.add_argument("-i", "--input", default="conv.inp")
    options = parser.parse_args(argv)

    calculation = FdmInp(options.input)
    filout = calculation.get_filout()
    if not filout:
        raise ValueError("Filout is missing")

    writer = FdmConvolutionInputs()
    generated_paths = writer.write(filout)
    for path in generated_paths:
        print(path)


if __name__ == "__main__":
    main()
