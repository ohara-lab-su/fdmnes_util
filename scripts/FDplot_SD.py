#!/usr/bin/env python3
"""``*_sdN.txt`` から指定した軌道群または軌道射影を描き、既定で ``SD.pdf`` に保存する。"""
import argparse

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


def main(argv=None):
    """SD を直接指定して、複素射影や f 軌道を含む一つのチャンネルを描く。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--year", type=int, choices=(2016, 2020, 2026))
    parser.add_argument("--ispin", type=int, choices=(1, 2), default=1)
    channel = parser.add_mutually_exclusive_group()
    channel.add_argument("--group", choices=("s", "p", "d", "f", "total"), default="p")
    channel.add_argument("--orbital", help="SD orbital name, e.g. '(2,0)' or 'fxyz'")
    parser.add_argument("--spin", choices=("up", "down"))
    parser.add_argument("--intdos", action="store_true")
    parser.add_argument("-o", "--output", default="SD.pdf")
    parser.add_argument("--nw", action="store_true")
    options = parser.parse_args(argv)
    if options.orbital and options.intdos:
        parser.error("--intdos requires an angular-momentum group or total")

    reader = FdmSd(
        options.input,
        format_year=options.year,
        ispin=options.ispin,
    ).select_reader()
    spins = (0,)
    if reader.get_ispin() == 2:
        spins = (0, 1)
    if options.spin == "up":
        spins = (0,)
    if options.spin == "down":
        if reader.get_ispin() != 2:
            parser.error("The SD file has no down-spin channel")
        spins = (1,)
    orbital = options.group
    if options.orbital is not None:
        orbital = options.orbital
    spin_labels = ("", "")
    if reader.get_ispin() == 2:
        spin_labels = (" up", " down")
    PlotFdmDos().plot_composite(
        reader,
        options.output,
        groups=((orbital,),),
        spins=spins,
        spin_labels=spin_labels,
        projected=options.orbital is not None,
        integrated=options.intdos,
        xlabel="Energy [eV]",
        show=not options.nw,
    )


if __name__ == "__main__":
    main()
