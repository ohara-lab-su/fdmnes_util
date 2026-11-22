#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SAE original: sae/commands/fdLDOSmulti.py
# K.NAKADA, kengo.nakada@gmail.com
# FDMNES sd*.txt plot program, multiplot version.
# 2015.08.18 startup
# 2018.08.17 Python2/3 両対応
# Copyright 2015, Kengo NAKADA. MIT license.
"""Plot three FDMNES site-resolved LDOS spectra.

This editable example reproduces the three-panel p-LDOS layout of the
original SAE script. The input prefix and output name can be changed
without modifying the installed library.
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


def main(argv=None):
    """Read three site files and save a multi-panel LDOS figure.

    Args:
        argv: Optional command-line arguments.

    Returns:
        pathlib.Path: Generated figure path.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="BaTiO3_R3m")
    parser.add_argument("--year", type=int, choices=(2016, 2020))
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--output", default="LDOSmulti.pdf")
    parser.add_argument(
        "--all-formats",
        action="store_true",
        help="Save EPS, PDF, and PNG, as in the SAE original.",
    )
    parser.add_argument("--orbital", default="p")
    options = parser.parse_args(argv)

    # The original script compares sd0, sd1, and sd2 from one calculation.
    prefix = Path(options.input)
    spectrum = FdmTxt(f"{prefix}.txt")
    readers = []
    labels = []

    for site_index in range(3):
        filename = f"{prefix}_sd{site_index}.txt"
        reader = FdmSd(filename, format_year=options.year).select_reader()
        readers.append(reader)
        labels.append(f"sd{site_index}, {options.orbital}")

    plotter = PlotFdmDos()
    if options.all_formats:
        # The suffix is replaced by each requested image format.
        return plotter.save_multiple_formats(
            readers,
            labels,
            options.output,
            edge_energy=spectrum.get_eedge(),
            fermi_energy=spectrum.get_efermi(),
            orbital=options.orbital,
            emin=options.emin,
            emax=options.emax,
        )

    return plotter.plot_multiple_sites(
        readers,
        labels,
        options.output,
        edge_energy=spectrum.get_eedge(),
        fermi_energy=spectrum.get_efermi(),
        orbital=options.orbital,
        emin=options.emin,
        emax=options.emax,
    )


if __name__ == "__main__":
    main()
