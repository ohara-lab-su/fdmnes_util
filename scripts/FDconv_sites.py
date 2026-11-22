#!/usr/bin/env python3
"""サイト別の生 XAS ``<Filout>_N.txt`` を指定して、合成・畳み込み用の ``conv.inp`` を書く。

各サイトの重みとシフトを入力に記述する。スペクトルの畳み込みは、生成した入力を使って FDMNES 本体で実行する。
"""
import argparse

from fdmnes_util.fdm_inp import FdmInp


def main(argv=None):
    """重みとシフトを指定し、サイトを合成する畳み込み入力を作る。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site",
        nargs=3,
        action="append",
        required=True,
        metavar=("XAS", "WEIGHT", "SHIFT"),
    )
    parser.add_argument("-o", "--output", default="combined_conv.txt")
    parser.add_argument("--input-file", default="conv.inp", help="Generated input file")
    parser.add_argument("--header", action="store_true")
    parser.add_argument("--energy-step", type=float, help="Output spacing in eV")
    parser.add_argument("--per-atom", action="store_true")
    options = parser.parse_args(argv)
    try:
        path = FdmInp.write_convolution(
            options.input_file,
            options.site,
            output=options.output,
            format_year=2026,
            header=options.header,
            energy_step=options.energy_step,
            per_atom=options.per_atom,
        )
    except ValueError as error:
        parser.error(str(error))
    print(path)


if __name__ == "__main__":
    main()
