"""2016 SD format: ordered n(l,m)/Intn(l,m)/n_l(l) data, spin aware."""
from pathlib import Path
import re
import numpy as np
class ReadFdmSd2016:
    def __init__(self,filename,*,ispin=1,weight=None):
        self.path=Path(filename)
        lines=self.path.read_text(errors='replace').splitlines()
        if len(lines)<2:raise ValueError('Incomplete SD file')
        self.header=lines[0].split()
        if not any('n(' in x for x in self.header):raise ValueError('Not 2016 SD format')
        self.ispin=int(ispin)
        if self.ispin not in (1,2):raise ValueError('ispin must be 1 or 2')
        labels=[int(n) for token in self.header for n in re.findall(r'n\((\d+),',token)]
        if not labels:raise ValueError('Cannot detect 2016 lmax')
        self.lmax=max(labels)
        self.values=np.loadtxt(self.path,skiprows=1,ndmin=2)
        ncol=1+self.ispin+sum((2*(2*l+1)+2)*self.ispin for l in range(self.lmax+1))
        if self.values.shape[1]!=ncol:
            raise ValueError(f'2016 SD column mismatch: {self.values.shape[1]} != {ncol}')
        if weight is not None:
            if not weight:raise ValueError('weight must be nonzero')
            self.values[:,1:]/=float(weight)
        self.energy=self.values[:,0].copy()
        n=len(self.energy)
        self._partial={};self._integrated_partial={};self._ldos={};self._intldos={}
        offset=1+self.ispin
        for l in range(self.lmax+1):
            for m in range(-l,l+1):
                for spin in range(self.ispin):
                    self._partial[(l,m,spin)]=self.values[:,offset];offset+=1
                    self._integrated_partial[(l,m,spin)]=self.values[:,offset];offset+=1
            for spin in range(self.ispin):
                self._ldos[(l,spin)]=self.values[:,offset];offset+=1
                self._intldos[(l,spin)]=self.values[:,offset];offset+=1
        self._total={s:sum(self._ldos[l,s] for l in range(self.lmax+1)) for s in range(self.ispin)}
        # Preserve SAE 2016 accumulation order: initial Int_t plus summed Intn_l.
        self._integrated_total={s:self.values[:,1+s]+sum(self._intldos[l,s] for l in range(self.lmax+1)) for s in range(self.ispin)}
    def get_eng(self):return self.energy
    def get_lmax(self):return self.lmax
    def get_ispin(self):return self.ispin
    def get_ldos(self,l=0,spin=0):return self._ldos[(('spdf'.index(l) if isinstance(l,str) else l),spin)]
    def get_intldos(self,l=0,spin=0):return self._intldos[(('spdf'.index(l) if isinstance(l,str) else l),spin)]
    def get_pdos(self,l=0,m=0,lm=None,spin=0):
        orbital={'s':(0,0),'px':(1,1),'py':(1,-1),'pz':(1,0),
                 'dxy':(2,-2),'dyz':(2,-1),'dz2':(2,0),'dxz':(2,1),'dx2-y2':(2,2)}
        if lm is not None:l,m=orbital[lm.lower().replace('_','')]
        return self._partial[(l,m,spin)]
    def get_tdos(self,spin=0):return self._total[spin]
    def get_inttdos(self,spin=0):return self._integrated_total[spin]
