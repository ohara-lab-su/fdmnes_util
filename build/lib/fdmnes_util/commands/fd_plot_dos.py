import argparse
from fdmnes_util.read_fdm_sd import read_fdm_sd
from fdmnes_util.plot_fdm_dos import PlotFdmDos

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('sd_file');p.add_argument('--year',type=int,required=True)
    p.add_argument('-o','--output',default='DOS.pdf');p.add_argument('--intdos',action='store_true')
    args=p.parse_args(argv)
    PlotFdmDos().plot(read_fdm_sd(args.sd_file,format_year=args.year),args.output,integrated=args.intdos)
if __name__=='__main__':main()
