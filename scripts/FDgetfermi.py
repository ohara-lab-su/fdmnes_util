#!/usr/bin/env python3
"""Display the Fermi energy and absorption-edge energy of a calculation."""

import argparse

from fdmnes_util.read_fdm_bav import ReadFdmBav
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.read_fdm_txt import ReadFdmTxt


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
        input_file = ReadFdmInp(options.input)
        filout = input_file.get_filout()

    if not filout:
        raise ValueError("Filout is missing")

    spectrum = ReadFdmTxt(f"{filout}.txt")
    log = ReadFdmBav(f"{filout}_bav.txt").select_reader()

    print("E_Fermi")
    print(spectrum.get_efermi())
    print(f"E_Edge ({log.get_edge()})")
    print(spectrum.get_eedge())


if __name__ == "__main__":
    main()
