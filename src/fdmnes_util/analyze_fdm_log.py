#!/usr/bin/env python3
"""Analysis of cluster coordinates from an FDMNES _bav.txt calculation log."""
from importlib.resources import files
import numpy as np

class AnalyzeFdmLog:
    """AnalyzeFdmLogに関する処理を提供する。"""
    def __init__(self,reader):
        """__init__の処理を実行する。
        
        Args:
            reader: readerを指定する。
        
        Returns:
            処理結果。
        
        """
        self.reader=reader

    def positions(self):
        # FDMNES: Z posx posy posz ! dista ia igr ...
        """positionsの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        text=files('fdmnes_util').joinpath('atomic_symbols.list').read_text()
        periodic={int(row.split()[0]):row.split()[1] for row in text.splitlines()}
        source=self.reader.lines
        start=next((i for i,line in enumerate(source)
                    if 'Cluster: atom positions in order' in line),None)
        if start is None:
            raise ValueError('Cluster: atom positions section is missing')
        symbols=[]
        positions=[]
        for line in source[start+1:]:
            parts=line.split()
            if len(parts)<4:
                if symbols:
                    break
                continue
            try:
                atomic_number=int(parts[0])
                point=[float(component.replace('D','E')) for component in parts[1:4]]
                symbol=periodic[atomic_number]
            except (ValueError,IndexError,KeyError):
                if symbols:
                    break
                continue
            symbols.append(symbol)
            positions.append(point)
        if not symbols:
            raise ValueError('No atom positions in log cluster')
        return symbols,np.asarray(positions,dtype=float)
