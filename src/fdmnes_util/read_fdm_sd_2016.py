#!/usr/bin/env python3
"""Read the column-ordered FDMNES 2016 SD output format."""

import re
from pathlib import Path

import numpy as np


class ReadFdmSd2016:
    """Read DOS projections and spin channels from a 2016 SD file."""

    def __init__(self, filename, *, ispin=1, weight=None):
        """Load a 2016-format SD output.

        Args:
            filename: Path to an SD output file.
            ispin: Number of spin channels (one or two).
            weight: Optional normalization divisor.

        Raises:
            ValueError: If the input header or number of columns is invalid.
        """
        self.path = Path(filename)
        lines = self.path.read_text(errors="replace").splitlines()
        if len(lines) < 2:
            raise ValueError("Incomplete SD file")

        self.header = lines[0].split()
        found_orbital_header = False
        for token in self.header:
            if "n(" in token:
                found_orbital_header = True
                break
        if not found_orbital_header:
            raise ValueError("Not 2016 SD format")

        self.ispin = int(ispin)
        if self.ispin not in (1, 2):
            raise ValueError("ispin must be 1 or 2")

        labels = []
        for token in self.header:
            for number in re.findall(r"n\((\d+),", token):
                labels.append(int(number))
        if not labels:
            raise ValueError("Cannot detect 2016 lmax")
        self.lmax = max(labels)

        self.values = np.loadtxt(self.path, skiprows=1, ndmin=2)
        expected_columns = 1 + self.ispin
        for angular_momentum in range(self.lmax + 1):
            expected_columns += (2 * (2 * angular_momentum + 1) + 2) * self.ispin
        if self.values.shape[1] != expected_columns:
            raise ValueError(
                f"2016 SD column mismatch: {self.values.shape[1]} != {expected_columns}"
            )

        if weight is not None:
            if not weight:
                raise ValueError("weight must be nonzero")
            self.values[:, 1:] /= float(weight)

        self.energy = self.values[:, 0].copy()
        self._partial = {}
        self._integrated_partial = {}
        self._ldos = {}
        self._intldos = {}
        offset = 1 + self.ispin

        # The 2016 format stores one orbital and its integrated value
        # consecutively, then the l-projected values for each spin channel.
        for angular_momentum in range(self.lmax + 1):
            for magnetic_quantum_number in range(
                -angular_momentum, angular_momentum + 1
            ):
                for spin in range(self.ispin):
                    key = (angular_momentum, magnetic_quantum_number, spin)
                    self._partial[key] = self.values[:, offset]
                    offset += 1
                    self._integrated_partial[key] = self.values[:, offset]
                    offset += 1
            for spin in range(self.ispin):
                key = (angular_momentum, spin)
                self._ldos[key] = self.values[:, offset]
                offset += 1
                self._intldos[key] = self.values[:, offset]
                offset += 1

        self._total = {}
        self._integrated_total = {}
        for spin in range(self.ispin):
            total = np.zeros_like(self.energy)
            integrated_total = self.values[:, 1 + spin].copy()
            for angular_momentum in range(self.lmax + 1):
                key = (angular_momentum, spin)
                total += self._ldos[key]
                integrated_total += self._intldos[key]
            self._total[spin] = total
            self._integrated_total[spin] = integrated_total

    def get_eng(self):
        """Return the energy axis."""
        return self.energy

    def get_lmax(self):
        """Return the highest angular-momentum channel."""
        return self.lmax

    def get_ispin(self):
        """Return the number of spin channels."""
        return self.ispin

    def get_ldos(self, l=0, spin=0):
        """Return an angular-momentum-resolved DOS channel."""
        if isinstance(l, str):
            l = "spdf".index(l)
        return self._ldos[(l, spin)]

    def get_intldos(self, l=0, spin=0):
        """Return an integrated angular-momentum DOS channel."""
        if isinstance(l, str):
            l = "spdf".index(l)
        return self._intldos[(l, spin)]

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """Return an orbital-projected DOS channel."""
        orbitals = {
            "s": (0, 0),
            "px": (1, 1),
            "py": (1, -1),
            "pz": (1, 0),
            "dxy": (2, -2),
            "dyz": (2, -1),
            "dz2": (2, 0),
            "dxz": (2, 1),
            "dx2-y2": (2, 2),
        }
        if lm is not None:
            key = lm.lower().replace("_", "")
            l, m = orbitals[key]
        return self._partial[(l, m, spin)]

    def get_tdos(self, spin=0):
        """Return the total projected DOS for a spin channel."""
        return self._total[spin]

    def get_inttdos(self, spin=0):
        """Return integrated total projected DOS for a spin channel."""
        return self._integrated_total[spin]
