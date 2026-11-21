"""SD (2020.06.16-2) format: named orbital columns and Int(total)."""
from pathlib import Path
import numpy as np
class ReadFdmSd2020:
    _ORBITALS={'s':(0,0),'py':(1,-1),'pz':(1,0),'px':(1,1),
               'dxy':(2,-2),'dyz':(2,-1),'dz2':(2,0),'dxz':(2,1),'dx2-y2':(2,2)}
    _ALIASES={'p_y':'py','p_z':'pz','p_x':'px','d_xy':'dxy','d_yz':'dyz',
              'd_z2':'dz2','d_z^2':'dz2','d_xz':'dxz','d_x2-y2':'dx2-y2','d_x^2-y^2':'dx2-y2'}
    def __init__(self,filename,*,weight=None):
        self.path=Path(filename)
        lines=self.path.read_text(errors='replace').splitlines()
        if len(lines)<2:raise ValueError('Incomplete SD file')
        self.columns=lines[0].split()
        if len(self.columns) not in (5,10,17):
            raise ValueError(f'Not a 2020 SD header ({len(self.columns)} columns)')
        self.values=np.loadtxt(self.path,skiprows=1,ndmin=2)
        if self.values.shape[1]!=len(self.columns):raise ValueError('SD column count mismatch')
        if weight is not None:
            if not weight:raise ValueError('weight must be nonzero')
            self.values[:,1:]/=float(weight)
        self.energy=self.values[:,0].copy()
        self.lmax={5:0,10:1,17:2}[len(self.columns)]
        self.ispin=1
        self._fields=dict(zip(self.columns,self.values.T))
        if not {'Energy','s','Int(s)','total','Int(total)'}.issubset(self._fields):
            raise ValueError('Required SD columns absent')
    def get_eng(self):return self.energy
    def get_lmax(self):return self.lmax
    def get_ispin(self):return self.ispin
    def get_ldos(self,l=0,spin=0):
        if spin not in (0,'up','non','nonmag'):raise ValueError('2020 sample: non-spin SD columns')
        key=('s','p','d')[l] if isinstance(l,int) else l
        return self._fields[key]
    def get_intldos(self,l=0,spin=0):
        key=('s','p','d')[l] if isinstance(l,int) else l
        return self._fields[f'Int({key})']
    def get_pdos(self,l=0,m=0,lm=None,spin=0):
        if lm is not None:
            key=self._ALIASES.get(lm.lower(),lm.lower())
        else:
            key=next((key for key,val in self._ORBITALS.items() if val==(l,m)),None)
        if key not in self._fields:raise KeyError(f'Orbital absent: {key}')
        return self._fields[key]
    def get_tdos(self,spin=0):return self._fields['total']
    def get_inttdos(self,spin=0):return self._fields['Int(total)']
