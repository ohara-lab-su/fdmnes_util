#!/usr/bin/env python3
"""Plot convolved spectra from all-site FDMNES calculations."""

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.athena_nor import AthenaNor
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_txt import FdmTxt


def main(argv=None):
    """Execute the multiple-site XAS plotting command.

    Args:
        argv: Optional command-line arguments. Defaults to ``sys.argv``.

    Returns:
        pathlib.Path: Path to the generated PDF file.
    """
    parser = argparse.ArgumentParser(
        description="Plot FDMNES all-site convolved XAS spectra"
    )
    parser.add_argument("-i", "--input", default="read_pdb.inp")
    parser.add_argument(
        "-a",
        "--average",
        nargs="+",
        type=int,
        required=True,
        metavar="SITE",
    )
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--ymax", type=float)
    parser.add_argument("-f", "--fermi", action="store_true")
    # In the original FDplot_XASs.py, -o means 'observed'. It is a switch,
    # not the output filename. Keep that meaning.
    parser.add_argument("-o", "--obs", action="store_true")
    parser.add_argument("--output", default="XAS.pdf")
    options = parser.parse_args(argv)

    input_file = FdmInp(options.input)
    filout = input_file.get_filout()
    if not filout:
        parser.error("The input file does not contain the Filout keyword")

    base = Path(options.input).parent / filout
    first_site = options.average[0]
    raw_xas_path = Path(f"{base}_{first_site}.txt")
    raw_xas = FdmTxt(raw_xas_path)

    spectra = AnalyzeFdmXas.site_spectra(
        base,
        options.average,
        input_is_photon=input_file.get_energygpho(),
        fermi=options.fermi,
    )

    observed = None
    if options.obs:
        observed = []
        for site in options.average:
            # Athena measurements follow the file name used in SAE.
            observed_path = Path(f"{base}_{site}_obs.txt.nor")
            reader = AthenaNor(observed_path)
            observed.append(
                (reader.get_eng(), reader.get_nor(), f"obs. {site}")
            )

    fermi_position = raw_xas.get_eedge() + raw_xas.get_efermi()
    if options.fermi:
        fermi_position = 0.0

    plotter = PlotFdmXas()
    return plotter.plot_sites(
        spectra,
        options.output,
        observed=observed,
        xmin=options.emin,
        xmax=options.emax,
        ymax=options.ymax,
        fermi=options.fermi,
        fermi_position=fermi_position,
    )


if __name__ == "__main__":
    main()
