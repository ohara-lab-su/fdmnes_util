#!/usr/bin/env python3
# SAE original: sae/commands/FDfdm2vasp.py
# ---- Original SAE development history ----
# K.NAKADA, kengo.nakada@gmail.com
# 統合テスト兼、FDMNES --> VASP 変換
# 2018.08.17: Python2/3 両対応
# 2015.08.20: startup
# 既知の問題: 分子系の変換時のunit-cellのスケールがおかしい
# ---- End of original SAE history ----
"""Convert a FDMNES Crystal input file into a VASP POSCAR example.

This sample uses the file-oriented FdmInp class for FDMNES parsing.
ASE writes the VASP file; no POSCAR parser is duplicated here.
The original SAE script also attempted molecular structures, but this
example intentionally rejects Molecule inputs until their cell convention
can be established from the original implementation.
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp


def main() -> None:
    """Parse the example's arguments and convert the crystal structure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="read_pdb.inp")
    parser.add_argument("-i", "--input-file", dest="input_option")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    input_path = Path(args.input)
    if args.input_option is not None:
        input_path = Path(args.input_option)

    output_path = args.output
    if output_path is None:
        output_path = Path(str(input_path) + ".vasp")

    # The FDMNES-specific interpretation remains in its file class.
    input_file = FdmInp(input_path)
    atoms = input_file.get_crystal_atoms()

    # ASE provides the POSCAR writer; this project does not implement one.
    from ase.io import write

    write(str(output_path), atoms, format="vasp", direct=True)
    print(f"INPUT : {input_path}")
    print(f"OUTPUT: {output_path}")


if __name__ == "__main__":
    main()
