#!/usr/bin/env python3
# Original SAE source: FDconv_e2photoe.py
# SAE: Copyright Kengo NAKADA; SAE class library.
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2018.08.17
"""Write converted convolution spectrum with absolute photon energy."""
from pathlib import Path
import numpy as np
class WriteFdmPhotoenergy:
    """WriteFdmPhotoenergyに関する処理を提供する。"""
    def write(self, energy, intensity, filename):
        """writeの処理を実行する。
        
        Args:
            energy: energyを指定する。
            intensity: intensityを指定する。
            filename: filenameを指定する。
        
        Returns:
            処理結果。
        
        """
        if len(energy)!=len(intensity):
            raise ValueError('Energy and intensity lengths differ')
        out=Path(filename)
        np.savetxt(out,np.column_stack((energy,intensity)),fmt='%13.5f  %14.10f',header='Energy    <xanes>')
        return out
