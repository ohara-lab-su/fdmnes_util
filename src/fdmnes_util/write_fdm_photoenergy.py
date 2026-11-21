"""Write converted convolution spectrum with absolute photon energy."""
from pathlib import Path
import numpy as np
class WriteFdmPhotoenergy:
    def write(self, energy, intensity, filename):
        if len(energy)!=len(intensity):raise ValueError('Energy and intensity lengths differ')
        out=Path(filename)
        np.savetxt(out,np.column_stack((energy,intensity)),fmt='%13.5f  %14.10f',header='Energy    <xanes>')
        return out
