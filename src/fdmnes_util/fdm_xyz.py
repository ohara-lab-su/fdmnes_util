#!/usr/bin/env python3
# Original SAE source: FDbav2xyz.py
# SAE: Copyright Kengo NAKADA; SAE class library.
# SAE: 2018.08.21
# SAE: 2015.06.24 startup
"""Write XYZ output from the parsed FDMNES calculation log."""
from pathlib import Path
class FdmXyz:
    """WriteFdmXyzに関する処理を提供する。"""
    def write(self, symbols, positions,filename):
        """writeの処理を実行する。
        
        Args:
            symbols: symbolsを指定する。
            positions: positionsを指定する。
            filename: filenameを指定する。
        
        Returns:
            処理結果。
        
        """
        if len(symbols)!=len(positions):
            raise ValueError('Atom/coordinate count mismatch')
        out=Path(filename)
        lines=[str(len(symbols)),'']
        lines += [f'{s} {x:.10f} {y:.10f} {z:.10f}' for s,(x,y,z) in zip(symbols,positions)]
        out.write_text('\n'.join(lines)+'\n')
        return out
