#!/usr/bin/env python3
"""Move generated FDMNES result files into an archive directory."""

import argparse

from fdmnes_util.fdm_result_files import FdmResultFiles
from fdmnes_util.fdm_inp import FdmInp


def main(argv=None):
    """Move files belonging to the selected Filout prefix.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Archive FDMNES results")
    parser.add_argument("-i", "--input", default="read_pdb.inp")
    parser.add_argument("-d", "--destination", required=True)
    options = parser.parse_args(argv)

    input_file = FdmInp(options.input)
    filout = input_file.get_filout()
    if not filout:
        raise ValueError("Filout is missing")

    result_files = FdmResultFiles(filout)
    moved_paths = result_files.move(options.destination)
    for path in moved_paths:
        print(f"MOVE: {path}")


if __name__ == "__main__":
    main()
