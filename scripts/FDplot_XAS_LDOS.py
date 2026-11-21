#!/usr/bin/env python3
"""Plot FDMNES XAS and orbital LDOS for a selected absorbing site."""

import argparse
from pathlib import Path

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_txt import FdmTxt


def main(argv=None):
    """Reproduce the stacked XAS/LDOS plot of ``FDplot_XAS_LDOS.py``.

    Args:
        argv: Optional command-line arguments.

    Returns:
        pathlib.Path: Path of the generated PDF.
    """
    parser = argparse.ArgumentParser(
        description="Plot FDMNES XAS and site-resolved orbital LDOS"
    )
    parser.add_argument("-i", "--inpname", default="read_pdb.inp")
    parser.add_argument("-f", "--filout")
    parser.add_argument("-a", "--atom", type=int, default=0)
    parser.add_argument("--fermi", action="store_true")
    parser.add_argument("--year", type=int, required=True, choices=[2016, 2020])
    parser.add_argument("--output")
    options = parser.parse_args(argv)

    inp_path = Path(options.inpname)
    inp = FdmInp(inp_path)
    filout = options.filout
    if not filout:
        filout = inp.get_filout()
    if not filout:
        parser.error("Filout is absent; specify --filout")

    prefix = inp_path.parent / filout
    raw_xas = FdmTxt(Path(f"{prefix}.txt"))
    conv = FdmConv(Path(f"{prefix}_conv.txt"))
    sd = FdmSd(
        Path(f"{prefix}_sd{options.atom}.txt"),
        format_year=options.year,
        ispin=inp.get_ispin(),
    ).select_reader()

    xas_energy = AnalyzeFdmXas.energy_reference(
        conv.get_eng(),
        raw_xas,
        input_is_photon=inp.get_energygpho(),
        fermi=options.fermi,
    )
    orbital_series = []
    orbitals = ("s", "p", "d")
    for orbital_index, orbital in enumerate(orbitals):
        if orbital_index > sd.get_lmax():
            continue

        density = sd.get_ldos(orbital)
        dos_energy = AnalyzeFdmXas.energy_reference(
            sd.get_eng(),
            raw_xas,
            input_is_photon=inp.get_energygpho(),
            fermi=options.fermi,
        )
        label = f"{options.atom}-{orbital}"
        orbital_series.append((label, dos_energy, density))

    # Photon-energy axes show the absolute Fermi marker. A relative axis
    # places the Fermi level at zero.
    fermi_position = raw_xas.get_eedge() + raw_xas.get_efermi()
    if options.fermi:
        fermi_position = 0.0

    output = options.output
    if not output:
        output = f"XAS_LDOS{options.atom}.pdf"

    plotter = PlotFdmXasLdos()
    return plotter.plot(
        (xas_energy, conv.get_xas()),
        orbital_series,
        output,
        fermi_position=fermi_position,
        fermi=options.fermi,
    )


if __name__ == "__main__":
    main()
