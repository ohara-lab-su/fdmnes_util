#!/usr/bin/env python3
# Copyright Kengo NAKADA; SAE class library.
# SAE: sae/commands/FDvasp2fdm.py
"""Convert a VASP POSCAR file to a FDMNES structure section.

This editable example demonstrates the external vasp_util POSCAR reader and
FDMNES structure writer. It also generates the original SAE calculation input template as read_pdb.inp.
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_structure import FdmStructure


def main() -> int:
    """Read POSCAR and write a FDMNES structure file.

    Returns:
        int: Zero when conversion succeeds.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", nargs="?")
    parser.add_argument("-i", "--input", "--ipput", default="POSCAR")
    parser.add_argument("-m", "--mol", action="store_true")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()

    input_path = Path(args.name or args.input)
    if not input_path.is_file():
        alternative_path = Path(str(input_path) + ".vasp")
        if alternative_path.is_file():
            input_path = alternative_path
        else:
            parser.error(f"POSCAR file not found: {input_path}")

    if args.output is None:
        output_path = Path(str(input_path) + ".fdmnes")
    else:
        output_path = Path(args.output)

    from vasp_util.vasp_poscar import VaspPoscar

    structure = VaspPoscar(str(input_path))
    writer = FdmStructure(structure)
    writer.write(output_path, molecule=args.mol)
    FdmInp.write("read_pdb.inp", structure_writer=writer, molecule=args.mol)
    print(writer.render(molecule=args.mol), end="")
    print(f"Written: {output_path}")
    print("Written: read_pdb.inp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
