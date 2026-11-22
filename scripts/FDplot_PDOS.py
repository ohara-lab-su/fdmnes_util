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
"""計算入力 ``*.inp`` または ``*_sdN.txt`` を指定して PDOS 図を保存する。

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
    """PDOS の各パネルと指定した XAS の重ね描きを作る。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 主図の保存先。
    """
    workflow = DosPlotWorkflow(projected=True)
    parser = workflow.build_parser()
    options = parser.parse_args(argv)
    return workflow.plot(PlotFdmDos(), options)


if __name__ == "__main__":
    main()
