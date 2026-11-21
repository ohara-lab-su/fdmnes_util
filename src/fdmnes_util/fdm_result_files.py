"""File-set operations across one FDMNES run; not an individual parser."""
from pathlib import Path
import shutil
class FdmResultFiles:
    def __init__(self,filout):
        self.filout=Path(filout)
        if not self.filout.name:raise ValueError('Empty Filout')
    def outputs(self):
        folder=self.filout.parent;stem=self.filout.name
        out=[folder/f'{stem}{suffix}' for suffix in ('.txt','_bav.txt','_conv.txt')]
        out+=sorted(folder.glob(stem+'_sd*.txt'))
        out += [folder/name for name in ('fdmnes_error.txt','fdm.out','PBS_log')]
        return [p for p in out if p.exists() and p.is_file()]
    def move_outputs(self):
        return [p for p in self.outputs() if p.name.startswith(self.filout.name)
                and (p.name.endswith('.txt'))]
    def clean(self):
        files=self.outputs()
        for path in files:path.unlink()
        return files
    def move(self,destination):
        dst=Path(destination);dst.mkdir(parents=True,exist_ok=True)
        output=[]
        for path in self.move_outputs():output.append(Path(shutil.move(str(path),str(dst/path.name))))
        return output
