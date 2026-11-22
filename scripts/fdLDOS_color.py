#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SAE original: sae/commands/fdLDOS_color.py
# Original author: Kengo NAKADA (Copyright 2015; MIT).
# Based on FDplot_LDOS.py (2015.11.30).
# The original colored the valence band for core-transition illustrations.
# 2018.08.17: Python 2/3 compatibility update.
# The original header is preserved here as a historical record; this sample
# uses the new fdmnes_util file-oriented API instead of the SAE API.
"""Plot an orbital LDOS with the occupied states shaded in gray.

This editable example reproduces the occupied-state shading used by SAE's
``fdLDOS_color.py``. Other plotting combinations from that script remain
outside the scope of this example.
"""

import argparse

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


def main(argv=None):
    """Load a site-resolved SD file and plot its occupied LDOS.

    Args:
        argv: Optional command-line arguments for embedding or tests.

    Returns:
        pathlib.Path: Saved figure path.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to the FDMNES *_sd*.txt file")
    parser.add_argument("--year", type=int)
    parser.add_argument("--orbital", default="p")
    parser.add_argument("--edge-offset", type=float, default=0.0)
    parser.add_argument("--fermi", type=float, default=0.0)
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--dmax", type=float)
    parser.add_argument("--output", default="LDOS_color.pdf")
    options = parser.parse_args(argv)

    sd_file = FdmSd(options.input, format_year=options.year).select_reader()
    plotter = PlotFdmDos()
    result = plotter.plot_occupied_ldos(
        sd_file,
        options.output,
        orbital=options.orbital,
        edge_offset=options.edge_offset,
        fermi_position=options.fermi,
        emin=options.emin,
        emax=options.emax,
        dmax=options.dmax,
    )
    return result


if __name__ == "__main__":
    main()
