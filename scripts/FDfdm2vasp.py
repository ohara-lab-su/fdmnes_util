#!/usr/bin/env python3
# SAE source: sae/commands/FDfdm2vasp.py
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# 統合テスト兼、FDMNES --> VASP 変換
#
################################################################################
# History
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.08.20
#  startup
#  既知の問題: 分子系の変換時のunit-cellのスケールがおかしい
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""FDMNES の計算入力 ``*.inp`` の Crystal または Molecule 節を読んで POSCAR に変換する。

FdmInp が計算入力を読み、ASE が POSCAR を書き出す。分子の場合は座標尺度を使って原子位置を求め、真空層を設けたセルを作る。
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_structure import FdmStructure


def main() -> None:
    """指定した構造を変換して POSCAR に保存する。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?")
    parser.add_argument(
        "-i", "--input", "--input-file", dest="input_option", default="read_pdb.inp"
    )
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument(
        "--vacuum",
        type=float,
        default=10.0,
        help="Molecule-only padding on each side, in angstroms (default: 10)",
    )
    args = parser.parse_args()

    input_path = Path(args.input or args.input_option)

    output_path = args.output
    if output_path is None:
        output_path = Path(str(input_path) + ".vasp")

    try:
        atoms = FdmStructure.fdm_to_atoms(input_path, vacuum=args.vacuum)
    except ValueError as error:
        parser.error(str(error))

    # ASE provides the POSCAR writer; this project does not implement one.
    from ase.io import write

    write(str(output_path), atoms, format="vasp", direct=True)
    print(f"INPUT : {input_path}")
    print(f"OUTPUT: {output_path}")


if __name__ == "__main__":
    main()
