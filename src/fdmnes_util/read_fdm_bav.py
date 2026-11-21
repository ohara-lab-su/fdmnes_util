#!/usr/bin/env python3
"""Select a version-specific reader for an FDMNES calculation log."""

import re
from pathlib import Path


class ReadFdmBav:
    """Inspect a ``_bav.txt`` header and select its version-specific parser."""

    def __init__(self, filename):
        """Read the revision marker from a calculation log.

        Args:
            filename: Calculation-log filename.

        Raises:
            ValueError: If the revision marker or its year cannot be found.
        """
        self.path = Path(filename)
        self.lines = self.path.read_text(errors="replace").splitlines()
        self.revision = None
        for line in self.lines:
            if "FDMNES program," in line:
                self.revision = line.strip()
                break
        if self.revision is None:
            raise ValueError("Missing FDMNES revision line")
        years = re.findall(r"\b(?:19|20)\d{2}\b", self.revision)
        if not years:
            raise ValueError(f"Unknown FDMNES version: {self.revision}")
        self.year = int(years[-1])

    def select_reader(self):
        """Return the implementation selected by the revision year.

        Notes:
            The 2020 designation reflects the SAE format. It does not
            establish equivalence with the output of FDMNES 2022.
        """
        if self.year <= 2016:
            from .read_fdm_bav_2016 import ReadFdmBav2016

            return ReadFdmBav2016(self.path)
        from .read_fdm_bav_2020 import ReadFdmBav2020

        return ReadFdmBav2020(self.path)
