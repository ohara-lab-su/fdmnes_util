#!/usr/bin/env python3
# SAE source: sae/commands/FDxyz2fdm.py.
# Original author: Kengo NAKADA; Copyright 2015, MIT.
# Original history:
# 2018.08.21 Python2/3 両対応
# 2015.06.30 == None --> is None
# 2015.05.18 startup
"""Convert a standard XYZ molecule to a FDMNES molecule section.

This editable example shows how to combine a file parser with the FDMNES
structure formatter. Unlike SAE's original command, OpenMX MD files and the
full calculation-input template are not yet supported.
"""

import argparse
from pathlib import Path

from fdmnes_util.fdm_structure import FdmStructure
from fdmnes_util.xyz import Xyz


def main() -> None:
    """Read XYZ coordinates and write a FDMNES molecule section."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Standard XYZ file")
    parser.add_argument("--output", type=Path, help="Output .fdmnes file")
    args = parser.parse_args()

    xyz = Xyz(args.input)
    molecule = FdmStructure.render_xyz_molecule(xyz.symbols, xyz.positions)

    if args.output is None:
        output = args.input.with_suffix(".fdmnes")
    else:
        output = args.output

    output.write_text(molecule, encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
