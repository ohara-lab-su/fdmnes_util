#!/usr/bin/env python3
# SAE source: sae/commands/FDpbd2fdm.py.
# ---- Original SAE header (verbatim) ----
# PDB to FDMNES crystal 情報
#
#  using ASE version
#
# 2015.08.20
#  関数分離(ごく一部だけASE分離)
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""Convert a PDB structure into a FDMNES structural input section.

The input is classified as a crystal when a CRYST1 record exists. Without
CRYST1, the original Cartesian coordinates are written as a molecule.
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_structure import FdmStructure
from fdmnes_util.pdb import Pdb


def main() -> None:
    """Read a PDB file and write the corresponding FDMNES structure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("POSCAR.pdb"))
    parser.add_argument("-i", "--ipput", dest="input_option", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    input_path = args.input
    if args.input_option is not None:
        input_path = args.input_option

    structure = Pdb(input_path)
    if structure.molecule:
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
