#!/usr/bin/env python3
"""Detect FDMNES _bav.txt revision without guessing a modern format."""
from pathlib import Path
import re
class ReadFdmBav:
    def __init__(self,filename):
        self.path=Path(filename)
        self.lines=self.path.read_text(errors='replace').splitlines()
        self.revision=next((line.strip() for line in self.lines if 'FDMNES program,' in line),None)
        if self.revision is None:raise ValueError('Missing FDMNES revision line')
        years=re.findall(r'\b(?:19|20)\d{2}\b',self.revision)
        if not years:raise ValueError(f'Unknown FDMNES version: {self.revision}')
        self.year=int(years[-1])
    def select_reader(self):
        # 2020 is the name of the format in SAE, not a claim of 2022 compatibility.
        if self.year<=2016:
            from .read_fdm_bav_2016 import ReadFdmBav2016
            return ReadFdmBav2016(self.path)
        from .read_fdm_bav_2020 import ReadFdmBav2020
        return ReadFdmBav2020(self.path)
