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
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


def main(argv=None):
    """Average site PDOS and optional convolved XAS, then save a figure.

    Args:
        argv: Optional command-line arguments for testing or reuse.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sd_files", nargs="*", help="SD files to average")
    parser.add_argument("--year", type=int)
    parser.add_argument("--orbitals", nargs="+", default=["s", "p_z"])
    parser.add_argument("--spin", type=int, default=0)
    parser.add_argument(
        "--sp",
        action="store_true",
        help="SAE s/p orbital grouping: s, p_z, and (p_y, p_x)",
    )
    parser.add_argument(
        "--spd",
        action="store_true",
        help="SAE s/p/d orbital grouping (the original default)",
    )
    parser.add_argument(
        "--input",
        help="FDMNES .inp file used to determine the energy reference",
    )
    parser.add_argument(
        "--fermi",
        action="store_true",
        help="Use Fermi-relative energy instead of photon energy (SAE --fermi)",
    )
    parser.add_argument(
        "--label",
        help="Label prefix for orbital curves (SAE --label)",
    )
    parser.add_argument(
        "-a",
        "--atom",
        type=int,
        default=0,
        help="Site index used in default orbital labels (SAE --atom)",
    )
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
    parser.add_argument(
        "--energy-offset",
        type=float,
        default=0.0,
        help="Shift all plotted DOS and XAS energy axes by this value in eV",
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
    parser.add_argument("-o", "--output")
    parser.add_argument("--outsuffix", default="")
    parser.add_argument("--dosweight", type=float)
    parser.add_argument("-x", "--xas", action="store_true")
    parser.add_argument("-b", "--broad", action="store_true")
    parser.add_argument("--nw", action="store_true")
    options = parser.parse_args(argv)

    reference_raw = None
    if not options.sd_files:
        prefixes = (
            "R5_fdm_ad_on_67/ZrO2Pd",
            "R5_fdm_ad_on_68/ZrO2Pd",
            "R5_fdm_ad_on_72/ZrO2Pd",
        )
        options.sd_files = [f"{prefix}_sd{options.atom}.txt" for prefix in prefixes]
        if options.input is None:
            options.input = "R5_fdm_ad_on_67/read_pdb.inp"
        reference_raw = f"{prefixes[0]}.txt"
        if options.xas_files is None and (options.xas or options.broad):
            options.xas_files = [f"{prefix}_conv.txt" for prefix in prefixes]
        if options.raw_xas_files is None and options.broad:
            options.raw_xas_files = [f"{prefix}.txt" for prefix in prefixes]
        if not options.sp:
            options.spd = True
    elif options.xas or options.broad:
        if options.xas_files is None:
            parser.error("--xas or --broad with explicit SD files requires --xas-files")
        if options.broad and options.raw_xas_files is None:
            parser.error("--broad with explicit SD files requires --raw-xas-files")

    # Reproduce the orbital blocks defined in the original SAE script.
    # A custom --orbitals selection keeps the simple ungrouped layout.
    orbital_groups = None
    if options.sp and options.spd:
        parser.error("--sp and --spd cannot be specified together")
    if options.sp:
        orbital_groups = [
            ["s"],
            ["p_z"],
            ["p_y", "p_x"],
        ]
        options.orbitals = ["s", "p_z", "p_y", "p_x"]
    if options.spd:
        orbital_groups = [
            ["s"],
            ["p_y", "p_z", "p_x"],
            ["d_xy", "d_yz", "d_3z2-r2", "d_xz", "d_x2-y2"],
        ]
        options.orbitals = [
            "s",
            "p_y",
            "p_z",
            "p_x",
            "d_xy",
            "d_yz",
            "d_3z2-r2",
            "d_xz",
            "d_x2-y2",
        ]

    readers = []
    for filename in options.sd_files:
        reader_options = {"format_year": options.year}
        if options.dosweight is not None:
            reader_options["weight"] = options.dosweight
        sd_file = FdmSd(filename, **reader_options)
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
        # The SAE script labels each orbital as <atom>-<orbital> by default.
        # An explicit --label replaces the atom prefix, not the orbital name.
        if options.label is None:
            label_prefix = str(options.atom)
        else:
            label_prefix = options.label

        curve_label = f"{label_prefix}-{orbital}"
        orbital_data.append((curve_label, energy, density))

    # Validate the number of paired files before reading any XAS output.
    xas_data = None
    if options.xas_files is not None:
        if len(options.xas_files) != len(options.sd_files):
            parser.error("The number of --xas-files must match the number of SD files")

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

    # SAE determines the energy reference from the input calculation mode
    # and the edge/Fermi metadata in the unbroadened XAS file.
    energy_offset = options.energy_offset
    fermi_position = None
    xlabel = "Photon Energy [eV]"
    if options.input is not None:
        if options.raw_xas_files is not None:
            reference_raw = options.raw_xas_files[0]
        if reference_raw is None:
            parser.error("--input requires --raw-xas-files for energy metadata")

        input_file = FdmInp(options.input)
        reference_spectrum = FdmTxt(reference_raw)
        reference_shift, absolute_fermi = analyzer.energy_reference(
            input_file,
            reference_spectrum,
            fermi=options.fermi,
        )
        energy_offset += reference_shift
        # フェルミ基準の軸では縦線も原点に移し、ユーザー指定のシフトを適用する。
        fermi_position = options.energy_offset
        if not options.fermi:
            fermi_position += absolute_fermi
        else:
            xlabel = "Energy above Fermi [eV]"
    else:
        if options.fermi:
            parser.error("--fermi requires --input and --raw-xas-files")

    plotter = PlotFdmAverage()
    plotter.plot(
        orbital_data,
        options.output or f"PDOS{options.atom}{options.outsuffix}.pdf",
        xas_data=xas_data,
        raw_xas_data=raw_xas_data,
        emin=options.emin,
        emax=options.emax,
        dmax=options.dmax,
        ymax=options.ymax,
        energy_offset=energy_offset,
        orbital_groups=orbital_groups,
        fermi_position=fermi_position,
        xlabel=xlabel,
        extra_formats=options.output is None,
        show=not options.nw,
    )


if __name__ == "__main__":
    main()
