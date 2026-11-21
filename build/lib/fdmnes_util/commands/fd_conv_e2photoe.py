import argparse
from pathlib import Path
from fdmnes_util.read_fdm_inp import ReadFdmInp
from fdmnes_util.read_fdm_txt import ReadFdmTxt
from fdmnes_util.read_fdm_conv import ReadFdmConv
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.write_fdm_photoenergy import WriteFdmPhotoenergy

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('-i','--inp',default='read_pdb.inp')
    p.add_argument('-t','--text');p.add_argument('-c','--conv')
    p.add_argument('-f','--fermi',action='store_true');args=p.parse_args(argv)
    inp=ReadFdmInp(args.inp)
    if inp.get_energygpho():raise ValueError('Input already uses PhotonEnergy')
    base=args.text.removesuffix('.txt') if args.text else inp.get_filout()
    convbase=args.conv.removesuffix('_conv.txt') if args.conv else base
    raw=ReadFdmTxt(base+'.txt');conv=ReadFdmConv(convbase+'_conv.txt')

    energy,intensity=AnalyzeFdmXas.photon_energy(conv,raw,subtract_fermi=args.fermi,fermi_energy=raw.get_efermi())
    output=WriteFdmPhotoenergy().write(energy,intensity,convbase+'_conv_photoe.txt')
    print(output)
if __name__=='__main__':main()
