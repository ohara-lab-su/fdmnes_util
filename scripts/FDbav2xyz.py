#!/usr/bin/env python3
# SAE source: sae/commands/FDbav2xyz.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
#
# *_bav.txt to xyz format
#
#
################################################################################
#
# 2018.08.21
#  Python2/3 両対応
#
# 2015.06.24 startup
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""Extract atomic positions from a FDMNES calculation log as XYZ data."""
# fmt: on

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_log import AnalyzeFdmLog
from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.fdm_xyz import FdmXyz


def main(argv=None):
    """Load one calculation log and generate an XYZ file or print XYZ data.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Convert FDMNES log to XYZ")
    parser.add_argument("name", nargs="?", help="Output prefix or *_bav.txt file")
    parser.add_argument("-i", "--input", help="Output prefix or *_bav.txt file")
    parser.add_argument("-s", "--std", action="store_true")
    options = parser.parse_args(argv)

    name = options.name or options.input
    if name:
        log_path = Path(name)
        if log_path.suffix != ".txt":
            log_path = Path(f"{name}_bav.txt")
    else:
        log_path = Path("Cu_bav.txt")
        if not log_path.is_file():
            candidates = sorted(
                path for path in Path.cwd().glob("*_bav.txt") if path.is_file()
            )
            if len(candidates) != 1:
                parser.error("Specify --input when there is no unique BAV file")
            log_path = candidates[0]

    # The log reader handles year-specific output formats.
    log = FdmBav(log_path).select_reader()
    analyzer = AnalyzeFdmLog(log)
    symbols, coordinates = analyzer.positions()

    writer = FdmXyz()
    if options.std:
        print(writer.render(symbols, coordinates), end="")
    else:
        output_name = f"{str(log_path).removesuffix('_bav.txt')}.xyz"
        output_path = writer.write(symbols, coordinates, output_name)
        print(output_path)


if __name__ == "__main__":
    main()
