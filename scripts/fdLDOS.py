#!/usr/bin/env python3
"""Create an LDOS plot from a version-specific FDMNES SD file."""

import argparse

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_sd import fdm_sd


def main(argv=None):
    """Read an SD file and draw its local density of states.

    Args:
        argv: Optional command-line argument sequence.

    Returns:
        pathlib.Path: Path to the created figure.
    """
    parser = argparse.ArgumentParser(description="Plot FDMNES LDOS")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("-o", "--output", default="LDOS.pdf")
    parser.add_argument("--intdos", action="store_true")
    options = parser.parse_args(argv)

    if options.input.endswith(".txt"):
        sd_path = options.input
    else:
        sd_path = f"{options.input}_sd0.txt"

    reader = fdm_sd(sd_path, format_year=options.year)
    plotter = PlotFdmDos()
    return plotter.plot(
        reader,
        options.output,
        integrated=options.intdos,
    )


if __name__ == "__main__":
    main()
