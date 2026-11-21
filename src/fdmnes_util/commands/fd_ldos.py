#!/usr/bin/env python3
"""Single LDOS plot through the versioned file-reader and plotter classes."""
import argparse
from fdmnes_util.read_fdm_sd import read_fdm_sd
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('-i','--input',required=True)
    parser.add_argument('--year',required=True,type=int)
    parser.add_argument('-o','--output',default='LDOS.pdf')
    parser.add_argument('--intdos',action='store_true')
    args=parser.parse_args(argv)
    file=args.input if args.input.endswith('.txt') else args.input+'_sd0.txt'
    sd=read_fdm_sd(file,format_year=args.year)
    return PlotFdmDos().plot(sd,args.output,integrated=args.intdos)
if __name__=='__main__':main()
