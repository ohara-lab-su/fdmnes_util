#!/usr/bin/env python3
# SAE source: sae/commands/FDplot_XASs.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#   *_{1,2,3,,,}_conv.txt plot program
#
#  allsite で出力した XAS の結果(_conv.txt) をまとめてプロット
#
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.07.01 fdXAS startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""Plot convolved spectra from all-site FDMNES calculations."""
# fmt: on

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.athena_nor import AthenaNor
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.fdmfile import Fdmfile


def main(argv=None):
    """Execute the multiple-site XAS plotting command.

    Args:
        argv: Optional command-line arguments. Defaults to ``sys.argv``.

    Returns:
        pathlib.Path: Path to the generated PDF file.
    """
    parser = argparse.ArgumentParser(
        description="Plot FDMNES all-site convolved XAS spectra"
    )
    parser.add_argument("-i", "--input")
    parser.add_argument(
        "-a",
        "--average",
        nargs="+",
        type=int,
        required=True,
        metavar="SITE",
    )
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--ymax", type=float)
    parser.add_argument("-f", "--fermi", action="store_true")
    # In the original FDplot_XASs.py, -o means 'observed'. It is a switch,
    # not the output filename. Keep that meaning.
    parser.add_argument("-o", "--obs", action="store_true")
    parser.add_argument("--output", default="XAS.pdf")
    options = parser.parse_args(argv)

    input_path = Fdmfile.select_input(options.input)
    input_file = FdmInp(input_path)
    filout = input_file.get_filout()
    if not filout:
        parser.error("The input file does not contain the Filout keyword")

    base = input_path.parent / filout
    first_site = options.average[0]
    raw_xas_path = Path(f"{base}_{first_site}.txt")
    raw_xas = FdmTxt(raw_xas_path)

    spectra = AnalyzeFdmXas.site_spectra(
        base,
        options.average,
        input_is_photon=input_file.get_energygpho(),
        fermi=options.fermi,
    )

    observed = None
    if options.obs:
        observed = []
        for site in options.average:
            # Athena measurements follow the file name used in SAE.
            observed_path = Path(f"{base}_{site}_obs.txt.nor")
            reader = AthenaNor(observed_path)
            observed.append((reader.get_eng(), reader.get_nor(), f"obs. {site}"))

    fermi_position = raw_xas.get_eedge() + raw_xas.get_efermi()
    if options.fermi:
        fermi_position = 0.0

    plotter = PlotFdmXas()
    return plotter.plot_sites(
        spectra,
        options.output,
        observed=observed,
        xmin=options.emin,
        xmax=options.emax,
        ymax=options.ymax,
        fermi=options.fermi,
        fermi_position=fermi_position,
    )


if __name__ == "__main__":
    main()
