#!/usr/bin/env python3
"""Plot XAS and site-resolved LDOS as a vertically stacked figure."""

from pathlib import Path


class PlotFdmXasLdos:
    """Draw XAS and orbital-resolved LDOS using prepared numerical arrays."""

    def plot(self, xas, orbital_spectra, output, *, fermi_position=None, fermi=False):
        """Write an XAS + orbital LDOS figure.

        Args:
            xas: Tuple of energy and absorption arrays.
            orbital_spectra: Iterable of (orbital, energy, LDOS) tuples.
            output: Output file path.
            fermi_position: Reference energy marker on every axis, when known.
            fermi: Whether the energy axis is relative to the Fermi level.

        Returns:
            pathlib.Path: Path to the generated figure.

        Raises:
            ValueError: If no orbital spectra were supplied.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        series = list(orbital_spectra)
        if not series:
            raise ValueError("At least one orbital spectrum is required")

        figure, axes = plt.subplots(
            len(series) + 1,
            1,
            figsize=(7.0, 9.89),
            sharex=True,
        )
        energy, intensity = xas
        axes[-1].plot(energy, intensity, linewidth=2, label="XAS")
        axes[-1].set_ylabel("Absorption [arb. unit]")
        axes[-1].set_ylim(bottom=0)
        axes[-1].legend(loc="lower right")

        # In the original command the XAS panel is at the bottom.
        # The orbital panels are arranged s, p, d upwards from it.
        for index, (orbital, energy, density) in enumerate(series):
            axis = axes[-2 - index]
            axis.plot(energy, density, linewidth=2, label=orbital)
            axis.set_ylabel("LDOS")
            axis.set_ylim(bottom=0)
            axis.legend(loc="upper right")

        if fermi:
            axes[-1].set_xlabel("Energy above Fermi [eV]")
        else:
            axes[-1].set_xlabel("Photon energy [eV]")

        for axis in axes:
            if fermi_position is not None:
                axis.axvline(fermi_position, color="black", linewidth=1)

        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)
