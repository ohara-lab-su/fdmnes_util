"""FDMNES convolution spectrum (filout_conv.txt)."""
from pathlib import Path
import numpy as np
class ReadFdmConv:
    def __init__(self,filename):
        self.path=Path(filename)
        with self.path.open() as file:self.header=file.readline().strip()
        self.values=np.loadtxt(self.path,skiprows=1,ndmin=2)
        self.energy=self.values[:,0]
        self.xas=self.values[:,1:]
    def get_eng(self):return self.energy
    def get_xas(self,spin=0):return self.xas[:,spin]
