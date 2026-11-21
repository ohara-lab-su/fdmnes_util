#!/usr/bin/env python3
"""Display the Fermi energy and absorption-edge energy of a calculation."""

import argparse

from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_txt import FdmTxt


def main(argv=None):
    """Read the required files and display the calculated energies.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Report FDMNES energies")
    parser.add_argument("-i", "--input", default="read_pdb.inp")
    parser.add_argument("--name", help="Output prefix overriding Filout")
    options = parser.parse_args(argv)

    if options.name:
        filout = options.name
    else:
        input_file = FdmInp(options.input)
        filout = input_file.get_filout()

    if not filout:
        raise ValueError("Filout is missing")

    spectrum = FdmTxt(f"{filout}.txt")
    log = FdmBav(f"{filout}_bav.txt").select_reader()

    print("E_Fermi")
    print(spectrum.get_efermi())
    print(f"E_Edge ({log.get_edge()})")
    print(spectrum.get_eedge())


if __name__ == "__main__":
    main()
