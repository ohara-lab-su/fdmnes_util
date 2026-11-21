#!/usr/bin/env python3
"""Remove the generated FDMNES files belonging to the selected calculation.

The input file is preserved. This script illustrates how to combine the
input-file reader and the result-file manager. Modify the parameters to suit
your calculation directory before using it in a research workflow.
"""

import argparse

from fdmnes_util.fdm_result_files import FdmResultFiles
from fdmnes_util.read_fdm_inp import ReadFdmInp


def main(argv=None):
    """Remove the output files corresponding to ``Filout``.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Remove FDMNES result files")
    parser.add_argument("-i", "--input", default="read_pdb.inp")
    options = parser.parse_args(argv)

    input_file = ReadFdmInp(options.input)
    filout = input_file.get_filout()
    if not filout:
        raise ValueError("The FDMNES input file has no Filout value")

    results = FdmResultFiles(filout)
    deleted_files = results.clean()
    for path in deleted_files:
        print(f"DELETE: {path}")


if __name__ == "__main__":
    main()
