#!/usr/bin/env python3
"""Plot a FDMNES XAS spectrum from the calculation's output files.

The numerical data are read by file-specific readers; the plot class handles
Matplotlib. This script can be copied and adapted for each research project.
"""

import argparse

from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt


def main(argv=None):
    """Read one calculated spectrum and save its figure.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Plot FDMNES XAS")
    parser.add_argument("filout", help="FDMNES output-file prefix")
    parser.add_argument("-o", "--output", default="XAS.pdf")
    parser.add_argument("--broad", action="store_true")
    options = parser.parse_args(argv)

    if options.broad:
        spectrum = FdmConv(f"{options.filout}_conv.txt")
    else:
        spectrum = FdmTxt(f"{options.filout}.txt")

    energy = spectrum.get_eng()
    absorption = spectrum.get_xas()
    plot_data = [(energy, absorption, options.filout)]
    plotter = PlotFdmXas()
    plotter.plot(plot_data, options.output)


if __name__ == "__main__":
    main()
