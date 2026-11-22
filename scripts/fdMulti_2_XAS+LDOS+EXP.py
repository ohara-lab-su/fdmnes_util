#!/usr/bin/env python3
# SAE source: sae/commands/fdMulti_2_XAS+LDOS+EXP.py
# ---- Original SAE header (verbatim, including original shebang) ----
# #!/usr/bin/env python
# # Copyright Kengo NAKADA; SAE class library.
# #   print "NAME",name
# from __future__ import print_function
# from sae.athena.nor import ReadAthenaNor
# from sae.fdmnes.conv import ReadFdmConv
# from sae.fdmnes.sd import ReadFdmSd
# from sae.fdmnes.txt import ReadFdmTxt
#
# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# ################################################################################
# # K.NAKADA, kengo.nakada@gmail.com
# #
# # FDMNES
# # *_conv.txt plot program
# #
# # Athena のデーターと一緒に比較する
# #
# ################################################################################
# #
# # 2015.06.30
# #  == None --> is None
# #
# # 2015.05.21 startup
# #
# ################################################################################
# ################################################################################
# __author__ = "Kengo NAKADA"
# __maintainer__ = "Kengo NAKADA"
# __credits__ = ["Kengo NAKADA"]
# __email__ = "kengo.nakada@gmail.com"
# __copyright__ = "Copyright 2015, Kengo NAKADA"
# __license__ = "MIT"
# ---- End of original SAE header ----
"""Compare FDMNES XAS, Athena experiment, and p-LDOS in two panels.

This editable example generalizes the original Cu-specific SAE script.
The original experiment scaling (1/39) and vertical offset (0.015)
are configurable, as is the calculated photon-energy offset (4.5 eV).
"""

import argparse
from pathlib import Path

from fdmnes_util.athena_nor import AthenaNor
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos


def main() -> None:
    """Read four source files and write a combined XAS/LDOS figure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conv", type=Path, default=Path("Cu_conv.txt"))
    parser.add_argument("--txt", type=Path, default=Path("Cu.txt"))
    parser.add_argument("--sd", type=Path, default=Path("Cu_sd0.txt"))
    parser.add_argument(
        "--experiment",
        type=Path,
        default=Path("Cu_K_Cu_foil_Si311_50ms_140625.txt.nor"),
    )
    parser.add_argument("--year", type=int, choices=[2016, 2020])
    parser.add_argument("--energy-offset", type=float, default=4.5)
    parser.add_argument("--experiment-scale", type=float, default=39.0)
    parser.add_argument("--experiment-offset", type=float, default=0.015)
    parser.add_argument("--xmin", type=float, default=8968.0)
    parser.add_argument("--xmax", type=float, default=9015.0)
    parser.add_argument("--output", type=Path, default=Path("XAS.pdf"))
    args = parser.parse_args()

    if args.experiment_scale == 0:
        parser.error("--experiment-scale must not be zero")

    conv = FdmConv(args.conv)
    raw = FdmTxt(args.txt)
    sd = FdmSd(args.sd, format_year=args.year).select_reader()
    measured = AthenaNor(args.experiment)

    edge = raw.get_eedge()
    fermi = raw.get_efermi()
    if edge is None or fermi is None:
        raise ValueError("FDMNES raw XAS must provide E_edge and E_fermi")

    # Each FDMNES output has its own energy grid. Do not substitute
    # the convolution grid for the raw XAS or SD energy grid.
    photon_offset = edge + args.energy_offset
    calculated_energy = conv.get_eng() + photon_offset
    raw_energy = raw.get_eng() + photon_offset
    ldos_energy = sd.get_eng() + photon_offset
    measured_absorption = (
        measured.get_nor() / args.experiment_scale + args.experiment_offset
    )

    plotter = PlotFdmXasLdos()
    output = plotter.plot_experiment_ldos(
        calculated_energy=calculated_energy,
        calculated_absorption=conv.get_xas(),
        raw_energy=raw_energy,
        raw_absorption=raw.get_xas(),
        observed_energy=measured.get_eng(),
        observed_absorption=measured_absorption,
        ldos_energy=ldos_energy,
        ldos_density=sd.get_ldos(l="p"),
        fermi_energy=photon_offset + fermi,
        output=args.output,
        xmin=args.xmin,
        xmax=args.xmax,
    )
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
