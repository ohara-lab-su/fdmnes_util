#!/usr/bin/env python3
"""FDMNES utility module: fd bav2xyz."""
import argparse
from pathlib import Path
from fdmnes_util.read_fdm_bav import ReadFdmBav
from fdmnes_util.analyze_fdm_log import AnalyzeFdmLog
from fdmnes_util.write_fdm_xyz import WriteFdmXyz

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('-s','--std',action='store_true')
    args=p.parse_args(argv)
    path=Path(args.name)
    if path.suffix!='.txt':path=Path(args.name+'_bav.txt')
    symbols,coords=AnalyzeFdmLog(ReadFdmBav(path).select_reader()).positions()
    if args.std:
        print(len(symbols));print('')
        for symbol,point in zip(symbols,coords):print(symbol,*point)
    else:
        print(WriteFdmXyz().write(symbols,coords,str(path).removesuffix('_bav.txt')+'.xyz'))
if __name__=='__main__':main()
