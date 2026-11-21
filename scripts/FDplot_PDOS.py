#!/usr/bin/env python3
# SAE source: sae/commands/FDplot_PDOS.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#   特定原子の PDOS 多段組
#
#   平均化機能は付けていない
#   DOSやXANESの平均化が欲しいときは FDplot_XAS.py -a 1 2 3 -w 55 -x 10
#   などとして、FDplot_XAS.py を用いて、 filout_0.txt filout_0_sd0.txt を
#   作成してから -c -s オプションなどを用いてプロットする
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.09.11
#  spin 対応版
#
# 2015.09.08
#  DOS の最大レンジ自動取得
#
# 2015.09.08
#   DOS のウェイト追加
#
# 2015.09.08
#  conv, txt, sd の同名指定オプション --name を追加
#
# 2015.09.07
#  startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""Plot PDOS and optional XAS from an FDMNES calculation."""
# fmt: on

from fdmnes_util.dos_plot_sample import dos_plot_arguments, plot_dos_sample
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


def main(argv=None):
    """Create the PDOS panels and any requested XAS overlay.

    Args:
        argv: Optional command-line argument sequence.

    Returns:
        pathlib.Path: Main saved figure.
    """
    parser = dos_plot_arguments(projected=True)
    options = parser.parse_args(argv)
    return plot_dos_sample(PlotFdmDos(), options, projected=True)


if __name__ == "__main__":
    main()
