"""Raw XANES (filout.txt), not convolved."""
from pathlib import Path
import numpy as np
class ReadFdmTxt:
    def __init__(self, filename):
        self.path=Path(filename)
        lines=self.path.read_text(errors='replace').splitlines()
        if len(lines)<3:raise ValueError('FDMNES XAS file is incomplete')
        self.metadata=lines[0]
        self.header=lines[1].split()
        self.values=np.loadtxt(self.path,skiprows=2,ndmin=2)
        self.energy=self.values[:,0]
        self.xas=self.values[:,1:]
        try:
            self.edge_energy=float(lines[0].split()[0])
        except (ValueError,IndexError):self.edge_energy=None
        self.atomic_number=int(float(lines[0].split()[1])) if len(lines[0].split())>1 else None
        # FDMNES metadata: values preceding '=' correspond to keys following '='.
        tokens=lines[0].replace(',', ' ').split()
        self.parameters={}
        if '=' in tokens:
            separator=tokens.index('=')
            values=tokens[:separator]
            names=tokens[separator+1:]
            for key,value in zip(names,values):
                try:self.parameters[key]=float(value)
                except ValueError:continue
        self.fermi_energy=self.parameters.get('E_Fermi',0.0)
    def get_eng(self):return self.energy
    def get_xas(self,spin=0):return self.xas[:,spin]
    def get_xas_all(self):return self.xas
    def get_eedge(self):return self.edge_energy
    def get_efermi(self):return self.fermi_energy
