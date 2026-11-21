#!/usr/bin/env python3
"""Allsite convolution input generation via separate input/output classes."""
import argparse
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.write_fdm_convolution_inputs import WriteFdmConvolutionInputs

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('-i','--input',default='conv.inp')
    options=parser.parse_args(argv)
    filout=ReadFdmInp(options.input).get_filout()
    if not filout:raise ValueError('Filout is missing')
    for path in WriteFdmConvolutionInputs().write(filout):print(path)
if __name__=='__main__':main()
