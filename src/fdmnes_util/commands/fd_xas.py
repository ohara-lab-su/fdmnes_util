"""Single spectrum script: all analysis/plotting lives in classes."""
import argparse
from fdmnes_util.read_fdm_conv import ReadFdmConv
from fdmnes_util.plot_fdm_xas import PlotFdmXas

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('-i','--input',required=True)
    parser.add_argument('-o','--output',default='XAS.pdf')
    args=parser.parse_args(argv)
    name=args.input.removesuffix('_conv.txt')
    spectrum=ReadFdmConv(name+'_conv.txt')
    return PlotFdmXas().plot([(spectrum.get_eng(),spectrum.get_xas(),name)],args.output)
if __name__=='__main__':main()
