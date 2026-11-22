"""Read BAV self-consistency records verified against FDMNES 2026 output."""

import re

from .fdm_bav_2020 import FdmBav2020


class FdmBav2026(FdmBav2020):
    """Extend the 2020 BAV reader with SCF cycle and total-energy records.

    The common BAV fields and the file-loading API come from FdmBav2020.
    """

    def get_n_scf_loop(self) -> int:
        """Return the last reported SCF cycle number.

        Returns:
            int: Last SCF cycle number, or zero when no cycle was found.
        """
        if self.is_self_consistent():
            cycle = None
            pattern = re.compile(r"\s*Cycle\s+(\d+)\s*,\s*Fermi energy\s*=", re.I)
            for line in self.lines:
                match = pattern.match(line)
                if match:
                    cycle = int(match.group(1))
            if cycle is not None:
                return cycle
        return super().get_n_scf_loop()

    def get_scf_toten(self) -> list[float]:
        """Return the reported SCF total energies in log order.

        Returns:
            list[float]: SCF total energies in eV, or an empty list if none
                were reported.
        """
        energies = []
        if self.is_self_consistent():
            pattern = re.compile(
                r"\s*Total energy\s*=\s*"
                r"([-+]?\d+(?:\.\d*)?(?:[EeDd][-+]?\d+)?)\s+eV\s*,\s*Delta energy\s*="
            )
            for line in self.lines:
                match = pattern.match(line)
                if match:
                    energies.append(float(match.group(1).replace("D", "E").replace("d", "e")))
        return energies or super().get_scf_toten()
