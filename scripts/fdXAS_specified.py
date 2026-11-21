#!/usr/bin/env python3
"""Plot an explicitly selected FDMNES spectrum above the Fermi energy.

The original SAE example used the fixed input ``R3.0/Au``. The input
prefix is now configurable so that users can edit and reuse this example.
"""

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt


def main(argv=None):
    """Create the Fermi-relative XAS figure.

    Args:
        argv: Optional command-line arguments. If omitted, parse sys.argv.

    Returns:
        pathlib.Path: Location of the generated PDF.
    """
    parser = argparse.ArgumentParser(
        description="Plot a selected FDMNES spectrum above the Fermi energy"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="R3.0/Au",
        help="Input prefix without .txt or _conv.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="XAS.pdf",
        help="Output figure path",
    )
    options = parser.parse_args(argv)

    prefix = Path(options.input)
    raw_path = Path(f"{prefix}.txt")
    convolution_path = Path(f"{prefix}_conv.txt")

    raw_spectrum = FdmTxt(raw_path)
    convolved_spectrum = FdmConv(convolution_path)

    # Match the energy reference in the original SAE example.
    energy, absorption = AnalyzeFdmXas.fermi_relative_convolution(
        convolved_spectrum,
        raw_spectrum,
    )

    plotter = PlotFdmXas()
    spectra = [(energy, absorption, "XAS")]
    output = plotter.plot(
        spectra,
        options.output,
        xlabel="Energy above Fermi [eV]",
        ylabel="Absorption [arb. unit]",
    )
    return output


if __name__ == "__main__":
    main()
