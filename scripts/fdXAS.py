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
# 2015.06.30
#  == None --> is None
#
# 2015.05.21 startup
#
################################################################################
################################################################################
"""``*_conv.txt`` を読み、畳み込み XAS を描いて既定で ``XAS.pdf`` に保存する。"""
import argparse
from pathlib import Path

from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """畳み込みスペクトルを読み、XAS 図を保存する。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 保存したファイルのパス。
    """
    parser = argparse.ArgumentParser(description="Plot a convolved XAS")
    parser.add_argument("name", nargs="?")
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output", default="XAS.pdf")
    options = parser.parse_args(argv)

    suffix = "_conv.txt"
    name = options.name or options.input
    if name is None:
        path = Path("POSCAR_conv.txt")
        if not path.is_file():
            candidates = [
                candidate
                for candidate in Path.cwd().glob(f"*{suffix}")
                if candidate.is_file()
            ]
            if len(candidates) != 1:
                parser.error(
                    "Specify the input when no unique convolution file exists",
                )
            path = candidates[0]
    else:
        path = Path(f"{name.removesuffix(suffix)}{suffix}")

    spectrum = FdmConv(path)
    energy = spectrum.get_eng()
    absorption = spectrum.get_xas()

    plotter = PlotFdmXas()
    return plotter.plot_convolved(energy, absorption, options.output)


if __name__ == "__main__":
    main()
