#!/usr/bin/env python3
"""``<Filout>.txt`` と ``*_conv.txt`` を読み、フェルミ準位基準の XAS 図を保存する。

SAE 原版は入力接頭辞を R3.0/Au に固定していた。この例では別の接頭辞を指定して利用できる。
"""

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """フェルミ準位基準の XAS 図を作る。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        pathlib.Path: 生成した PDF のパス。
    """
    parser = argparse.ArgumentParser(
        description="Plot a selected FDMNES spectrum above the Fermi energy"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="R3.0/Au",
        help="Input prefix without .txt or _conv.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="XAS.pdf",
        help="Output figure path",
    )
    options = parser.parse_args(argv)

    prefix = Path(options.input)
    raw_path = Path(f"{prefix}.txt")
    convolution_path = Path(f"{prefix}_conv.txt")

    raw_spectrum = FdmTxt(raw_path)
    convolved_spectrum = FdmConv(convolution_path)

    # Match the energy reference in the original SAE example.
    energy, absorption = AnalyzeFdmXas.fermi_relative_convolution(
        convolved_spectrum,
        raw_spectrum,
    )

    plotter = PlotFdmXas()
    return plotter.plot_convolved(
        energy,
        absorption,
        options.output,
        specified=True,
    )


if __name__ == "__main__":
    main()
