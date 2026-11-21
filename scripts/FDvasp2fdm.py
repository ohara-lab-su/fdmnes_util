#!/usr/bin/env python3
"""Convert a VASP POSCAR file to a FDMNES structure section.

This editable example demonstrates the external vasp_util POSCAR reader and
FDMNES structure writer. It does not silently generate a full calculation
input template; the output contains only the structural section.
"""

import argparse
from pathlib import Path

from fdmnes_util.read_vasp_poscar import ReadVaspPoscar
from fdmnes_util.write_fdm_structure import WriteFdmStructure


def main() -> int:
    """Read POSCAR and write a FDMNES structure file.

    Returns:
        int: Zero when conversion succeeds.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", default="POSCAR")
    parser.add_argument("-m", "--mol", action="store_true")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()

    input_path = Path(args.input)
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

    structure = ReadVaspPoscar(str(input_path))
    writer = WriteFdmStructure(structure)
    writer.write(output_path, molecule=args.mol)
    print(writer.render(molecule=args.mol), end="")
    print(f"Written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
