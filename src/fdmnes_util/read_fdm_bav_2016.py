#!/usr/bin/env python3
"""Pre-2017 FDMNES cluster/log layout (separate reader)."""
from pathlib import Path
import re
import numpy as np
class ReadFdmBav2016:
    def __init__(self,filename):
        self.path=Path(filename)
        self.lines=self.path.read_text(errors='replace').splitlines()
        self.revision=next((x.strip() for x in self.lines if 'FDMNES program,' in x),'')
    def get_edge(self):
        line=next((x for x in self.lines if 'Threshold:' in x),'')
        return line.partition('Threshold:')[2].strip()
    def get_nspin(self):return 2 if any('Magnetic calculation' in x and 'Non-' not in x for x in self.lines) else 1
    def get_n_scf_loop(self):return sum('Begining of cycle' in x for x in self.lines)
    def get_scf_toten(self):
        result=[]
        for s in self.lines:
            if 'Unit cell energy' in s:
                nums=re.findall(r'[-+]?\d+(?:\.\d+)?(?:[EeDd][-+]?\d+)?',s)
                if nums:result.append(float(nums[-1].replace('D','E')))
        return result
    def get_position(self):
        # Cluster coordinates are parsed by the log analysis class.
        from .analyze_fdm_log import AnalyzeFdmLog
        return AnalyzeFdmLog(self).positions()[1]
    def get_atoms_index_j(self):
        from .analyze_fdm_log import AnalyzeFdmLog
        return AnalyzeFdmLog(self).positions()[0]
    def get_natom(self):return len(self.get_atoms_index_j())

    def get_e_edge(self):
        line=next((line for line in self.lines if line.lstrip().startswith('E_edge')),'')
        parts=line.split()
        if not line or len(parts)<3:return None
        try:return float(parts[2])
        except ValueError:return None

    def get_ngroup(self):
        import re
        line=next((line for line in self.lines if re.match(r'^\s*ngroup\s*=',line)),'')
        match=re.search(r'ngroup\s*=\s*(\d+)',line)
        return int(match.group(1)) if match else None

    def get_t(self):
        import numpy as np
        index=next((i for i,line in enumerate(self.lines)
                   if 'Transformation Crystal Bases' in line and 'Bases R2' in line),None)
        if index is None:return None
        return np.array([[float(x) for x in line.split()[:3]]
                         for line in self.lines[index+1:index+4]],dtype=float).T

    def get_lmax(self):
        begin=next((i for i,line in enumerate(self.lines) if line.lstrip().startswith('Excited atom,')),None)
        if begin is None:return None
        levels=[]
        for line in self.lines[begin+2:]:
            if line.lstrip().startswith('Atom type'):break
            parts=line.split()
            if len(parts)>=4:
                try:levels.append(int(parts[1]))
                except ValueError:continue
        return max(levels) if levels else None
