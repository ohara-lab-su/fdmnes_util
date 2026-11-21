#!/usr/bin/env python3
# Original SAE source: bav_2016.py
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2020.07.17
# SAE: 2016.08.01 以降に sd? のナンバリングルールが変わったのでそれに対する対応
# SAE: 2018.08.15
# SAE: 2015.09.11
# SAE: 2015.06.25
# SAE: 2015.06.23 startup
# SAE: Copyright Kengo NAKADA; SAE class library.
"""Read the FDMNES 2016 calculation-log format."""

import re
from pathlib import Path

import numpy as np


class ReadFdmBav2016:
    """Extract calculation information from a 2016-format ``_bav.txt`` file."""

    def __init__(self, filename):
        """Load the log file.

        Args:
            filename: Path to the FDMNES calculation log.
        """
        self.path = Path(filename)
        self.lines = self.path.read_text(errors="replace").splitlines()
        self.revision = ""
        for line in self.lines:
            if "FDMNES program," in line:
                self.revision = line.strip()
                break

    def get_edge(self):
        """Return the absorption-edge label in the log."""
        for line in self.lines:
            if "Threshold:" in line:
                return line.partition("Threshold:")[2].strip()
        return ""

    def get_nspin(self):
        """Return the number of spin channels reported by FDMNES."""
        for line in self.lines:
            if "Magnetic calculation" in line and "Non-" not in line:
                return 2
        return 1

    def get_n_scf_loop(self):
        """Count the SCF cycles recorded in the log."""
        count = 0
        for line in self.lines:
            if "Begining of cycle" in line:
                count += 1
        return count

    def get_scf_toten(self):
        """Return the sequence of unit-cell energies from SCF iterations."""
        energies = []
        pattern = r"[-+]?\d+(?:\.\d+)?(?:[EeDd][-+]?\d+)?"
        for line in self.lines:
            if "Unit cell energy" not in line:
                continue
            matches = re.findall(pattern, line)
            if matches:
                energy = float(matches[-1].replace("D", "E"))
                energies.append(energy)
        return energies

    def get_position(self):
        """Return Cartesian atomic positions from the log's cluster section."""
        from .analyze_fdm_log import AnalyzeFdmLog

        analyzer = AnalyzeFdmLog(self)
        positions = analyzer.positions()
        return positions[1]

    def get_atoms_index_j(self):
        """Return atomic numbers in the cluster section."""
        from .analyze_fdm_log import AnalyzeFdmLog

        analyzer = AnalyzeFdmLog(self)
        positions = analyzer.positions()
        return positions[0]

    def get_natom(self):
        """Return the number of atoms in the cluster section."""
        atoms = self.get_atoms_index_j()
        return len(atoms)

    def get_e_edge(self):
        """Return the numeric absorption-edge energy, if present."""
        for line in self.lines:
            if not line.lstrip().startswith("E_edge"):
                continue
            parts = line.split()
            if len(parts) < 3:
                return None
            try:
                return float(parts[2])
            except ValueError:
                return None
        return None

    def get_ngroup(self):
        """Return the number of atom groups, if recorded."""
        for line in self.lines:
            if re.match(r"^\s*ngroup\s*=", line):
                match = re.search(r"ngroup\s*=\s*(\d+)", line)
                if match is not None:
                    return int(match.group(1))
        return None

    def get_t(self):
        """Return the 3-by-3 crystal-basis transformation matrix."""
        index = None
        for current_index, line in enumerate(self.lines):
            if "Transformation Crystal Bases" in line and "Bases R2" in line:
                index = current_index
                break
        if index is None:
            return None
        rows = []
        for line in self.lines[index + 1 : index + 4]:
            row = []
            for value in line.split()[:3]:
                row.append(float(value))
            rows.append(row)
        return np.array(rows, dtype=float).T

    def get_lmax(self):
        """Return the maximum angular-momentum index in the atom listing."""
        begin = None
        for index, line in enumerate(self.lines):
            if line.lstrip().startswith("Excited atom,"):
                begin = index
                break
        if begin is None:
            return None
        levels = []
        for line in self.lines[begin + 2 :]:
            if line.lstrip().startswith("Atom type"):
                break
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                levels.append(int(parts[1]))
            except ValueError:
                continue
        if levels:
            return max(levels)
        return None
