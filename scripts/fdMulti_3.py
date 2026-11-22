#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SAE original: sae/commands/fdMulti_3.py
# K.NAKADA, kengo.nakada@gmail.com
# FDMNES sd*.txt plot program, multiplot version.
# 2015.08.18 startup
# 2018.08.17 Python2/3 両対応
# Copyright 2015, Kengo NAKADA. MIT license.
"""独立した三つの計算の ``<Filout>.txt`` と ``*_sdN.txt`` を読み、フェルミ準位を揃えて図を保存する。

SAE の例では Pd55_1、Pd55_5、FCC/Pd を比較した。接頭辞は利用者の計算結果に変更できる。各スペクトルは計算ごとのフェルミエネルギーで移動する。
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
    """三つの計算結果を読み、フェルミ準位を揃えた LDOS 図を保存する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        list[pathlib.Path]: EPS・PDF・PNG の保存先パス。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefixes", nargs="*", help="Three calculation prefixes")
    parser.add_argument("--year", type=int, choices=(2016, 2020))
    parser.add_argument("--site", type=int, default=0)
    parser.add_argument("--orbital", default="p")
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--dmax", type=float, default=5.0)
    parser.add_argument("--output", default="LDOSmulti")
    options = parser.parse_args(argv)

    if not options.prefixes:
        options.prefixes = ("Pd55_1", "Pd55_5", "FCC/Pd")
    if len(options.prefixes) != 3:
        parser.error("Specify three calculation prefixes")

    readers = []
    fermi_energies = []
    labels = []
    for prefix in options.prefixes:
        # The SD and TXT files must belong to the same calculation.
        sd_path = f"{prefix}_sd{options.site}.txt"
        txt_path = f"{prefix}.txt"
        reader = FdmSd(sd_path, format_year=options.year).select_reader()
        spectrum = FdmTxt(txt_path)
        readers.append(reader)
        fermi_energies.append(spectrum.get_efermi())
        labels.append(f"{Path(prefix).name}: {options.orbital}")

    plotter = PlotFdmDos()
    paths = [Path(options.output).with_suffix(ext) for ext in (".eps", ".pdf", ".png")]
    plotter.plot_three_calculations(
        readers,
        fermi_energies,
        labels,
        paths[0],
        orbital=options.orbital,
        emin=options.emin,
        emax=options.emax,
        density_max=options.dmax,
        extra_outputs=paths[1:],
    )
    return paths


if __name__ == "__main__":
    main()
