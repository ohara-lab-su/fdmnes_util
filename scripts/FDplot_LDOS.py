#!/usr/bin/env python3
"""Plot FDMNES density-of-states data from a site-resolved SD file."""

import argparse

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.read_fdm_sd import read_fdm_sd


def main(argv=None):
    """Read a selected SD format and create a DOS figure.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Plot FDMNES LDOS")
    parser.add_argument("sd_file")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("-o", "--output", default="LDOS.pdf")
    parser.add_argument("--intdos", action="store_true")
    options = parser.parse_args(argv)

    reader = read_fdm_sd(options.sd_file, format_year=options.year)
    plotter = PlotFdmDos()
    plotter.plot(reader, options.output, integrated=options.intdos)


if __name__ == "__main__":
    main()
