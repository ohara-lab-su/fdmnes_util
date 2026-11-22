#!/usr/bin/env python3
# SAE source: sae/commands/fdExp_comp_XAS.py
# ---- Original SAE history (verbatim) ----
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *_conv.txt plot program
#
# Athena のデーターと一緒に比較する
#
# 2015.06.30
#  == None --> is None
#
# 2015.05.21 startup
# ---- End of original SAE history ----
"""生 XAS ``<Filout>.txt``、``*_conv.txt``、Athena の ``*.nor`` を読み、計算と実験の比較図を保存する。

SAE 原版は Au のファイル名と軸範囲を固定していた。この例では対象ファイルをコマンドライン引数で指定できる。
"""

import argparse
from pathlib import Path

from fdmnes_util.athena_nor import AthenaNor
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main() -> None:
    """FDMNES と Athena のファイルを読み、比較図を保存する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", type=Path, default=Path("Au_conv.txt"))
    parser.add_argument("--txt", type=Path, default=Path("Au.txt"))
    parser.add_argument(
        "--experiment",
        type=Path,
        default=Path("Q14B_Au001_Aufoil.txt.nor"),
    )
    parser.add_argument("--output", type=Path, default=Path("XAS.pdf"))
    parser.add_argument("--xmin", type=float, default=11900.0)
    parser.add_argument("--xmax", type=float, default=12100.0)
    parser.add_argument("--ymax", type=float)
    args = parser.parse_args()

    calculated = FdmConv(args.input)
    raw = FdmTxt(args.txt)
    measured = AthenaNor(args.experiment)

    # The original SAE script converts the convolution axis to photon
    # energy by adding the absorption-edge energy from the raw XAS file.
    edge_energy = raw.get_eedge()
    if edge_energy is None:
        raise ValueError("The FDMNES XAS file has no edge energy")

    photon_energy = calculated.get_eng() + edge_energy
    plotter = PlotFdmXas()
    output_path = plotter.plot_experiment_comparison(
        calculated_energy=photon_energy,
        calculated_absorption=calculated.get_xas(),
        observed_energy=measured.get_eng(),
        observed_absorption=measured.get_nor(),
        output=args.output,
        xmin=args.xmin,
        xmax=args.xmax,
        ymax=args.ymax,
    )
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
