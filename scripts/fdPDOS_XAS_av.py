#!/usr/bin/env python3
# SAE original header (historical record; not executable code):
# #!/usr/bin/env python
# # Copyright Kengo NAKADA; SAE class library.
# #   print "NAME",name
#
# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# ################################################################################
# # K.NAKADA, kengo.nakada@gmail.com
# #
# # FDMNES
# #   特定原子の PDOS 多段組(FDplot_PDOS.py) をベースとした特化型スクリプト
# #   複数のデータを読み込んで平均化して DOS と XAS をプロット
# #   その都度編集せよ
# #
# ################################################################################
# #
# # 2018.08.17
# #  Python2/3 両対応
# #
# # 2015.09.09
# #
# ################################################################################
# ################################################################################
# __author__ = "Kengo NAKADA"
# __maintainer__ = "Kengo NAKADA"
# __credits__ = ["Kengo NAKADA"]
# __email__ = "kengo.nakada@gmail.com"
# __copyright__ = "Copyright 2015, Kengo NAKADA"
# __license__ = "MIT"
"""Example: average orbital-projected DOS from multiple FDMNES calculations.

This is a user-editable example, not a hidden command implementation.
The original SAE script used three hard-coded calculations. Supply the
corresponding SD paths explicitly to adapt this example to new systems.
"""

import argparse

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


def main(argv=None):
    """Average site PDOS and optional convolved XAS, then save a figure.

    Args:
        argv: Optional command-line arguments for testing or reuse.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sd_files", nargs="+", help="SD files to average")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--orbitals", nargs="+", default=["s", "p_z"])
    parser.add_argument("--spin", type=int, default=0)
    parser.add_argument(
        "--xas-files",
        nargs="+",
        help="Convolved XAS files corresponding to the calculations",
    )
    parser.add_argument(
        "--raw-xas-files",
        nargs="+",
        help="Unbroadened XAS files paired with --xas-files (SAE --broad)",
    )
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument(
        "--dmax",
        type=float,
        help="Upper limit of the DOS panels (SAE --dmax)",
    )
    parser.add_argument(
        "--ymax",
        type=float,
        help="Upper limit of the XAS panel (SAE --ymax)",
    )
    parser.add_argument("-o", "--output", default="PDOS_average.pdf")
    options = parser.parse_args(argv)

    readers = []
    for filename in options.sd_files:
        sd_file = FdmSd(filename, format_year=options.year)
        readers.append(sd_file.select_reader())

    analyzer = AnalyzeFdmAverage()
    orbital_data = []
    for orbital in options.orbitals:
        energy, density = analyzer.average(
            readers,
            "get_pdos",
            lm=orbital,
            spin=options.spin,
        )
        orbital_data.append((orbital, energy, density))

    # Validate the number of paired files before reading any XAS output.
    xas_data = None
    if options.xas_files is not None:
        if len(options.xas_files) != len(options.sd_files):
            parser.error(
                "The number of --xas-files must match the number of SD files"
            )

        # Each convolved spectrum retains its own energy grid. Averaging
        # is only meaningful when those grids agree point by point.
        xas_readers = []
        for filename in options.xas_files:
            xas_readers.append(FdmConv(filename))

        xas_data = analyzer.average(
            xas_readers,
            "get_xas",
            spin=options.spin,
        )

    raw_xas_data = None
    if options.raw_xas_files is not None:
        if options.xas_files is None:
            parser.error("--raw-xas-files requires --xas-files")
        if len(options.raw_xas_files) != len(options.sd_files):
            parser.error(
                "The number of --raw-xas-files must match the number of SD files"
            )

        # Unbroadened and convolved spectra have independent energy grids.
        # Average each family on its own grid; do not reuse the convolved axis.
        raw_xas_readers = []
        for filename in options.raw_xas_files:
            raw_xas_readers.append(FdmTxt(filename))

        raw_xas_data = analyzer.average(
            raw_xas_readers,
            "get_xas",
            spin=options.spin,
        )

    plotter = PlotFdmAverage()
    plotter.plot(
        orbital_data,
        options.output,
        xas_data=xas_data,
        raw_xas_data=raw_xas_data,
        emin=options.emin,
        emax=options.emax,
        dmax=options.dmax,
        ymax=options.ymax,
    )


if __name__ == "__main__":
    main()
