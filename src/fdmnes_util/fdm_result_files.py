#!/usr/bin/env python3
"""File-set operations across one FDMNES run; not an individual parser."""
from pathlib import Path
import shutil
class FdmResultFiles:
    """FdmResultFilesに関する処理を提供する。"""
    def __init__(self,filout):
        """__init__の処理を実行する。
        
        Args:
            filout: filoutを指定する。
        
        Returns:
            処理結果。
        
        """
        self.filout=Path(filout)
        if not self.filout.name:
            raise ValueError('Empty Filout')
    def outputs(self):
        """outputsの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        folder=self.filout.parent
        stem=self.filout.name
        out=[folder/f'{stem}{suffix}' for suffix in ('.txt','_bav.txt','_conv.txt')]
        out+=sorted(folder.glob(stem+'_sd*.txt'))
        out += [folder/name for name in ('fdmnes_error.txt','fdm.out','PBS_log')]
        return [p for p in out if p.exists() and p.is_file()]
    def move_outputs(self):
        """move_outputsの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        return [p for p in self.outputs() if p.name.startswith(self.filout.name)
                and (p.name.endswith('.txt'))]
    def clean(self):
        """cleanの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        files=self.outputs()
        for path in files:path.unlink()
        return files
    def move(self,destination):
        """moveの処理を実行する。
        
        Args:
            destination: destinationを指定する。
        
        Returns:
            処理結果。
        
        """
        dst=Path(destination)
        dst.mkdir(parents=True,exist_ok=True)
        output=[]
        for path in self.move_outputs():output.append(Path(shutil.move(str(path),str(dst/path.name))))
        return output
