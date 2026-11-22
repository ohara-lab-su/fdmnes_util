#!/usr/bin/env python3
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *_conv.txt plot program
#
################################################################################
#
# 2015.05.21 startup
#
################################################################################
################################################################################
"""``*.inp`` または ``*_sdN.txt`` を指定して LDOS を描き、既定で ``LDOS.pdf`` に保存する。"""
import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_sd import FdmSd

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """SD ファイルを読み、局所状態密度を描く。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 保存したファイルのパス。
    """
    parser = argparse.ArgumentParser(description="Plot FDMNES LDOS")
    parser.add_argument("name", nargs="?")
    parser.add_argument("-i", "--input")
    parser.add_argument("-a", "--atom", type=int)
    parser.add_argument("-l", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--year", type=int)
    parser.add_argument("-o", "--output", default="LDOS.pdf")
    parser.add_argument("--intdos", action="store_true")
    options = parser.parse_args(argv)

    name = options.name or options.input or "read_pdb.inp"
    path = Path(name)
    ispin = 1
    if path.suffix.lower() == ".inp":
        inp = FdmInp(path)
        filout = inp.get_filout()
        if not filout:
            parser.error(f"Missing Filout in {path}")
        atom = options.atom
        if atom is None:
            atom = 1
        sd_path = path.parent / f"{filout}_sd{atom}.txt"
        ispin = inp.get_ispin()
    elif path.suffix.lower() == ".txt":
        sd_path = path
    else:
        atom = options.atom
        if atom is None:
            atom = 0
        sd_path = Path(f"{name}_sd{atom}.txt")

    reader = FdmSd(sd_path, format_year=options.year, ispin=ispin).select_reader()
    plotter = PlotFdmDos()
    return plotter.plot_local(
        reader,
        options.output,
        orbit=options.l,
        integrated=options.intdos,
    )


if __name__ == "__main__":
    main()
