#!/usr/bin/env python3
"""Plot the p-orbital SD spectrum with the original axis-limit options."""

import argparse
from pathlib import Path

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import fdm_sd


def main(argv=None):
    """Generate LDOS figures using file and plot classes.

    The original SAE script had a hard-coded ``Pd6/Pd6`` prefix. This
    command instead resolves ``Filout`` from the selected FDMNES input file.

    Args:
        argv: Optional CLI argument sequence, for programmatic use.

    Returns:
        list[pathlib.Path]: Files written in the requested formats.
    """
    parser = argparse.ArgumentParser(
        description="Plot p-orbital FDMNES LDOS"
    )
    parser.add_argument("-i", "--input", default="read_pdb.inp")
    parser.add_argument("--year", type=int, choices=(2016, 2020), required=True)
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--dmax", type=float)
    parser.add_argument("--filout")
    parser.add_argument("--output-prefix", default="LDOS")
    parser.add_argument("--formats", nargs="+", default=("eps", "pdf", "png"))
    options = parser.parse_args(argv)

    input_path = Path(options.input)
    inp = FdmInp(input_path)
    filout = options.filout
    if filout is None:
        filout = inp.get_filout()
    if not filout:
        parser.error("Filout is absent; specify --filout")

    # Resolve the calculation outputs relative to the input file directory.
    # The SD index is zero in the original fdLDOS0_specified command.
    prefix = input_path.parent / filout
    sd_path = Path(f"{prefix}_sd0.txt")
    sd = fdm_sd(
        sd_path,
        format_year=options.year,
        ispin=inp.get_ispin(),
    )

    plotter = PlotFdmDos()
    saved_files = []
    for extension in options.formats:
        if extension not in ("eps", "pdf", "png"):
            parser.error(f"Unsupported image format: {extension}")

        output = Path(f"{options.output_prefix}.{extension}")
        saved_file = plotter.plot_single_orbital(
            sd,
            output,
            orbital="p",
            emin=options.emin,
            emax=options.emax,
            dmax=options.dmax,
        )
        saved_files.append(saved_file)

    return saved_files


if __name__ == "__main__":
    main()
