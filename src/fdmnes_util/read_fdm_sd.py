"""Explicit SD format dispatch: does not merge version-specific readers."""
from pathlib import Path
from .read_fdm_sd_2016 import ReadFdmSd2016
from .read_fdm_sd_2020 import ReadFdmSd2020

def read_fdm_sd(filename, *, format_year, ispin=1, weight=None):
    if format_year==2016:
        return ReadFdmSd2016(filename,ispin=ispin,weight=weight)
    if format_year==2020:
        return ReadFdmSd2020(filename,weight=weight)
    raise ValueError(f'Unverified SD layout for year {format_year}; explicitly choose tested format')
