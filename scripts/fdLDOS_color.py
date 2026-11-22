#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SAE original: sae/commands/fdLDOS_color.py
# Original author: Kengo NAKADA (Copyright 2015; MIT).
# Based on FDplot_LDOS.py (2015.11.30).
# The original colored the valence band for core-transition illustrations.
# 2018.08.17: Python 2/3 compatibility update.
# The original header is preserved here as a historical record; this sample
# uses the new fdmnes_util file-oriented API instead of the SAE API.
"""``*.inp`` または ``*_sdN.txt`` を指定して、フェルミ準位より下を灰色に塗った LDOS 図を保存する。

SAE の LDOS、TDOS、XAS の組み合わせと占有状態の塗り分けを扱います。
"""

import argparse
import sys

from fdmnes_util.dos_plot_sample import DosPlotSample
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


class OccupiedLdosSample:
    """``*.inp`` または ``*_sdN.txt`` を指定して、占有側を塗り分けた LDOS 図を作る。"""
    def run(self, argv=None):
        """計算入力から LDOS、TDOS、XAS を描く。

        Args:
            argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

        Returns:
            pathlib.Path: 保存したファイルのパス。
        """
        arguments = list(sys.argv[1:])
        if argv is not None:
            arguments = list(argv)
        if arguments and arguments[0].endswith(".txt"):
            return self._run_sd_file(arguments)

        sample = DosPlotSample(projected=False, shade_occupied=True)
        parser = sample.build_parser()
        return sample.plot(PlotFdmDos(), parser.parse_args(arguments))

    @staticmethod
    def _run_sd_file(argv):
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


def main(argv=None):
    return OccupiedLdosSample().run(argv)


if __name__ == "__main__":
    main()
