#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SAE original: sae/commands/fdLDOSmulti.py
# K.NAKADA, kengo.nakada@gmail.com
# FDMNES sd*.txt plot program, multiplot version.
# 2015.08.18 startup
# 2018.08.17 Python2/3 両対応
# Copyright 2015, Kengo NAKADA. MIT license.
"""生 XAS ``<Filout>.txt`` と3サイトの ``*_sdN.txt`` を読み、LDOS を並べた図を保存する。

SAE 原版の三段 p-LDOS を再現する。入力の接頭辞と出力名をサンプルで変更できる。
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """3サイトのファイルを読み、複数パネルの LDOS 図を保存する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 保存したファイルのパス。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="BaTiO3_R3m")
    parser.add_argument("--year", type=int, choices=(2016, 2020))
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--output")
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

    atoms = ("Ba", "Ba", "Ti")
    for site_index in range(3):
        filename = f"{prefix}_sd{site_index}.txt"
        reader = FdmSd(filename, format_year=options.year).select_reader()
        readers.append(reader)
        if prefix.name == "BaTiO3_R3m":
            labels.append(f"sd{site_index}, {atoms[site_index]}-{options.orbital}")
        else:
            labels.append(f"sd{site_index}, {options.orbital}")

    plotter = PlotFdmDos()
    if options.all_formats or options.output is None:
        # The suffix is replaced by each requested image format.
        return plotter.save_multiple_formats(
            readers,
            labels,
            options.output or "LDOSmulti.pdf",
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
