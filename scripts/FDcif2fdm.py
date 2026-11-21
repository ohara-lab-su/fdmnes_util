#!/usr/bin/env python3
# SAE source: sae/commands/FDcif2fdm.py.
# ---- Original SAE header (verbatim, comment text) ----
# VASP to FDMNES crystal 情報
#
# using ASE version
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""Convert CIF atomic structures to editable FDMNES structure sections.

The original SAE script stopped at ``bug version`` after loading the CIF.
This example completes the conversion using the public library classes.
"""

import argparse
from pathlib import Path

from fdmnes_util.cif import Cif
from fdmnes_util.fdm_structure import FdmStructure


def main() -> None:
    """Read a CIF file and save a FDMNES structural section."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("-i", "--ipput", dest="input_option", type=Path)
    parser.add_argument("-m", "--mol", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    input_path = Path("POSCAR.cif")
    if args.input is not None:
        input_path = args.input
    if args.input_option is not None:
        input_path = args.input_option

    structure = Cif(input_path)
    if args.mol:
        content = FdmStructure.render_xyz_molecule(
            structure.get_symbols(),
            structure.get_cartesian_positions(),
        )
    else:
        content = FdmStructure(structure).render()

    output_path = args.output
    if output_path is None:
        output_path = input_path.with_suffix(".fdmnes")

    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
