"""2026年版の Header 付き畳み込み XAS を読む。"""

from pathlib import Path

import numpy as np

from .fdm_conv_2016 import FdmConv2016


class FdmConv2026:
    """通常の XAS 列に加え、改訂情報と畳み込み条件を保持する。"""

    REVISION_HEADER = "# FDMNES program, Revision 5th of November 2026"

    def __init__(self, filename):
        self.path = Path(filename)
        with self.path.open(encoding="utf-8", errors="replace") as stream:
            self.preamble = []
            self.parameters = {}
            self.shifts = ()
            line = stream.readline().strip()
            while line.startswith("#"):
                self.preamble.append(line)
                values, _, field = line[1:].partition("=")
                field = field.strip()
                if field.startswith("E_edge,"):
                    names = [name.strip() for name in field.split(",")]
                    self.parameters.update(zip(names, map(float, values.split())))
                elif field == "Shifts":
                    self.shifts = tuple(map(float, values.split()))
                line = stream.readline().strip()
            self.header = line
            self.values = np.loadtxt(stream, ndmin=2)

        if len(self.values) == 0 or self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")
        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

    def get_eng(self):
        """Return the energy axis in the file-defined reference frame."""
        return self.energy

    def get_xas(self, spin=0):
        """Return the requested absorption column.

        Args:
            spin: Zero-based index of the absorption column.

        Returns:
            numpy.ndarray: Absorption intensity values.
        """
        return self.xas[:, spin]

    @staticmethod
    def write_spectrum(filename, spectrum):
        """平均スペクトルは共通の SAE 書式で保存する。"""
        return FdmConv2016.write_spectrum(filename, spectrum)
