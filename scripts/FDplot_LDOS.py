#!/usr/bin/env python3
# SAE source: sae/commands/FDplot_LDOS.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#   特定原子の LDOS 多段組
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.09.11
#  spin 対応版
#
# 2015.09.10
#  多数のオプション装備
#
# 2015.09.07
#  startup
#   スピン非対応
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""計算入力 ``*.inp`` または ``*_sdN.txt`` を指定して LDOS 図を保存する。

オプションに応じて生 XAS ``<Filout>.txt`` や畳み込み XAS ``*_conv.txt`` も使う。
"""
# fmt: on

from fdmnes_util.util.dos_plot_workflow import DosPlotWorkflow
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """LDOS の各パネルと指定した XAS の重ね描きを作る。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 主図の保存先。
    """
    workflow = DosPlotWorkflow(projected=False)
    parser = workflow.build_parser()
    options = parser.parse_args(argv)
    return workflow.plot(PlotFdmDos(), options)


if __name__ == "__main__":
    main()
