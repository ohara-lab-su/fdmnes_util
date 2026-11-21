"""FDgetfermi data reporting (reader-only CLI)."""
import argparse
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.read_fdm_bav import ReadFdmBav
from fdmnes_util.read_fdm_txt import ReadFdmTxt

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('-i','--input',default='read_pdb.inp')
    parser.add_argument('--name')
    options=parser.parse_args(argv)
    name=options.name or ReadFdmInp(options.input).get_filout()
    if not name:raise ValueError('Filout is missing')
    xas=ReadFdmTxt(name+'.txt')
    log=ReadFdmBav(name+'_bav.txt').select_reader()
    print('E_Fermi')
    print(xas.get_efermi())
    print('E_Edge ('+log.get_edge()+')')
    print(xas.get_eedge())
if __name__=='__main__':main()
