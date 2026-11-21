#!/usr/bin/env python3
"""Create an XAS plot from a convolved FDMNES spectrum."""

import argparse

from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv


def main(argv=None):
    """Read a convolution spectrum and save an XAS figure.

    Args:
        argv: Optional command-line argument sequence.

    Returns:
        pathlib.Path: Path to the created figure.
    """
    parser = argparse.ArgumentParser(description="Plot a convolved XAS")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="XAS.pdf")
    options = parser.parse_args(argv)

    prefix = options.input.removesuffix("_conv.txt")
    spectrum = FdmConv(f"{prefix}_conv.txt")
    energy = spectrum.get_eng()
    absorption = spectrum.get_xas()

    plot_data = [(energy, absorption, prefix)]
    plotter = PlotFdmXas()
    return plotter.plot(plot_data, options.output)


if __name__ == "__main__":
    main()
