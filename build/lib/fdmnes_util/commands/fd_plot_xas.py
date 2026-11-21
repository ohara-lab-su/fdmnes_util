import argparse
from fdmnes_util.read_fdm_txt import ReadFdmTxt
from fdmnes_util.read_fdm_conv import ReadFdmConv
from fdmnes_util.plot_fdm_xas import PlotFdmXas

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('filout');p.add_argument('-o','--output',default='XAS.pdf')
    p.add_argument('--broad',action='store_true');args=p.parse_args(argv)
    file=ReadFdmConv(args.filout+'_conv.txt') if args.broad else ReadFdmTxt(args.filout+'.txt')
    PlotFdmXas().plot([(file.get_eng(),file.get_xas(),args.filout)],args.output)
if __name__=='__main__':main()
