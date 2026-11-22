#!/usr/bin/env python3
"""``*.inp`` の Filout を使って ``*_sd0.txt`` を読み、p 軌道の LDOS 図を保存する。"""
import argparse
from pathlib import Path

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import FdmSd

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """ファイルクラスと描画クラスを組み合わせて LDOS 図を生成する。

    SAE 原版の接頭辞は Pd6/Pd6 固定。この例では指定入力の Filout を使う。

    Args:
        argv: コマンド名を除いた引数列。省略時はコマンドライン引数を使う。

    Returns:
        list[pathlib.Path]: 指定形式で保存したファイルのパスの並び。
    """
    parser = argparse.ArgumentParser(description="Plot p-orbital FDMNES LDOS")
    parser.add_argument("-i", "--input")
    parser.add_argument("--year", type=int, choices=(2016, 2020))
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--dmax", type=float)
    parser.add_argument("--filout")
    parser.add_argument("--output-prefix", default="LDOS")
    parser.add_argument("--formats", nargs="+", default=("eps", "pdf", "png"))
    options = parser.parse_args(argv)

    input_path = Path(options.input or "Pd6/read_pdb.inp")
    inp = FdmInp(input_path)
    filout = options.filout
    if filout is None:
        filout = inp.get_filout()
    if not filout:
        parser.error("Filout is absent; specify --filout")

    # Resolve the calculation outputs relative to the input file directory.
    # The SD index is zero in the original fdLDOS0_specified command.
    prefix = input_path.parent / filout
    sd_paths = [Path(f"{prefix}_sd0.txt")]
    divisor = None
    if options.input is None:
        # SAE の Pd6 例は五つの吸収サイトを足し、6 原子で割る。
        sd_paths = [Path(f"{prefix}_{site}_sd0.txt") for site in (1, 2, 3, 4, 5)]
        divisor = 6.0
    readers = [
        FdmSd(
            path,
            format_year=options.year,
            ispin=inp.get_ispin(),
        ).select_reader()
        for path in sd_paths
    ]

    plotter = PlotFdmDos()
    paths = []
    for extension in options.formats:
        if extension not in ("eps", "pdf", "png"):
            parser.error(f"Unsupported image format: {extension}")

        paths.append(Path(f"{options.output_prefix}.{extension}"))

    plotter.plot_single_orbital(
        readers,
        paths[0],
        orbital="p",
        emin=options.emin,
        emax=options.emax,
        dmax=options.dmax,
        divisor=divisor,
        extra_outputs=paths[1:],
    )
    return paths


if __name__ == "__main__":
    main()
