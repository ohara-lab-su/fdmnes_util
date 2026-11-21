#!/usr/bin/env python3
"""FDMNES utility module: fd clean."""
import argparse
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.fdm_result_files import FdmResultFiles

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('-i','--input',default='read_pdb.inp');args=p.parse_args(argv)
    filout=ReadFdmInp(args.input).get_filout()
    if not filout:raise ValueError('Missing Filout in input')
    for path in FdmResultFiles(filout).clean():print('DELETE:',path)
if __name__=='__main__':main()
