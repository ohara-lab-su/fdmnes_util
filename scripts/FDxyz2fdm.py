#!/usr/bin/env python3
# SAE source: sae/commands/FDxyz2fdm.py.
# Original author: Kengo NAKADA; Copyright 2015, MIT.
# Original history:
# 2018.08.21 Python2/3 両対応
# 2015.06.30 == None --> is None
# 2015.05.18 startup
"""標準 ``*.xyz`` を読み、FDMNES の Molecule 節を ``*.fdmnes`` などへ書き出す。

ファイルリーダーと FDMNES 構造ライターを組み合わせる例。対象は標準 XYZ と構造節の生成。
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_structure import FdmStructure
from fdmnes_util.xyz import Xyz


def main() -> None:
    """XYZ 座標を読み、FDMNES の Molecule 節を書き出す。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="?", help="Standard XYZ file")
    parser.add_argument("-i", "--input", type=Path, dest="input_option")
    parser.add_argument("--output", type=Path, help="Output .fdmnes file")
    args = parser.parse_args()

    input_path = args.input or args.input_option
    if input_path is None:
        parser.error("Specify a standard XYZ file")
    xyz = Xyz(input_path)
    molecule = FdmStructure.render_xyz_molecule(xyz.symbols, xyz.positions)

    if args.output is None:
        output = input_path.with_suffix(".fdmnes")
    else:
        output = args.output

    output.write_text(molecule, encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
