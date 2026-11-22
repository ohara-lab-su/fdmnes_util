#!/usr/bin/env python3
# SAE source: sae/commands/FDplot_LDOS.py
# fmt: off
# ---- SAE original header ----
# Copyright Kengo NAKADA; SAE class library.
################################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#   特定原子の LDOS 多段組
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.09.11
#  spin 対応版
#
# 2015.09.10
#  多数のオプション装備
#
# 2015.09.07
#  startup
#   スピン非対応
#
################################################################################
################################################################################
# ---- End of SAE original header ----
"""Plot LDOS and optional XAS from an FDMNES calculation."""
# fmt: on

from fdmnes_util.dos_plot_sample import DosPlotSample
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

__author__ = "Kengo NAKADA"
__maintainer__ = "Kengo NAKADA"
__credits__ = ["Kengo NAKADA"]
__email__ = "kengo.nakada@gmail.com"
__copyright__ = "Copyright 2015, Kengo NAKADA"
__license__ = "MIT"


def main(argv=None):
    """Create the LDOS panels and any requested XAS overlay.

    Args:
        argv: Optional command-line argument sequence.

    Returns:
        pathlib.Path: Main saved figure.
    """
    sample = DosPlotSample(projected=False)
    parser = sample.build_parser()
    options = parser.parse_args(argv)
    return sample.plot(PlotFdmDos(), options)


if __name__ == "__main__":
    main()
