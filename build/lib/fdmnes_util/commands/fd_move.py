import argparse
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.fdm_result_files import FdmResultFiles

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('-i','--input',default='read_pdb.inp')
    p.add_argument('-d','--destination',required=True)
    args=p.parse_args(argv)
    filout=ReadFdmInp(args.input).get_filout()
    if not filout:raise ValueError('Missing Filout')
    for path in FdmResultFiles(filout).move(args.destination):print('MOVE:',path)
if __name__=='__main__':main()
