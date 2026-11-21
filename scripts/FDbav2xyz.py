#!/usr/bin/env python3
"""Extract atomic positions from a FDMNES calculation log as XYZ data."""

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_log import AnalyzeFdmLog
from fdmnes_util.read_fdm_bav import ReadFdmBav
from fdmnes_util.write_fdm_xyz import WriteFdmXyz


def main(argv=None):
    """Load one calculation log and generate an XYZ file or print XYZ data.

    Args:
        argv: Optional command-line argument sequence.
    """
    parser = argparse.ArgumentParser(description="Convert FDMNES log to XYZ")
    parser.add_argument("name", help="Output prefix or *_bav.txt file")
    parser.add_argument("-s", "--std", action="store_true")
    options = parser.parse_args(argv)

    log_path = Path(options.name)
    if log_path.suffix != ".txt":
        log_path = Path(f"{options.name}_bav.txt")

    # The log reader handles year-specific output formats.
    log = ReadFdmBav(log_path).select_reader()
    analyzer = AnalyzeFdmLog(log)
    symbols, coordinates = analyzer.positions()

    if options.std:
        print(len(symbols))
        print("")
        for symbol, position in zip(symbols, coordinates):
            print(symbol, *position)
    else:
        output_name = f"{str(log_path).removesuffix('_bav.txt')}.xyz"
        writer = WriteFdmXyz()
        output_path = writer.write(symbols, coordinates, output_name)
        print(output_path)


if __name__ == "__main__":
    main()
