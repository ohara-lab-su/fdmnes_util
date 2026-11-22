#!/usr/bin/env python3
"""Plot XAS and site-resolved LDOS as a vertically stacked figure."""

from ._figure import save_figure


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
        return save_figure(figure, output)

    def plot_experiment_ldos(
        self,
        *,
        calculated_energy,
        calculated_absorption,
        raw_energy,
        raw_absorption,
        observed_energy,
        observed_absorption,
        ldos_energy,
        ldos_density,
        fermi_energy,
        output,
        xmin=None,
        xmax=None,
    ):
        """Draw the SAE two-panel XAS, experiment, and LDOS comparison.

        The upper panel contains p-LDOS. The lower panel contains
        broadened XAS, raw XAS, and the Athena measurement. Each
        spectrum retains its own energy grid.

        Args:
            calculated_energy: Photon energies of broadened XAS.
            calculated_absorption: Broadened absorption values.
            raw_energy: Photon energies of unbroadened XAS.
            raw_absorption: Unbroadened absorption values.
            observed_energy: Experimental photon energies.
            observed_absorption: Scaled and shifted experimental XAS.
            ldos_energy: Photon energies corresponding to the LDOS grid.
            ldos_density: p-orbital LDOS values.
            fermi_energy: Fermi level in photon-energy coordinates.
            output: Destination figure filename.
            xmin: Optional lower photon-energy limit.
            xmax: Optional upper photon-energy limit.

        Returns:
            pathlib.Path: Saved figure path.

        Raises:
            ValueError: If a spectrum has mismatched axis/value lengths.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        spectra = [
            (calculated_energy, calculated_absorption),
            (raw_energy, raw_absorption),
            (observed_energy, observed_absorption),
            (ldos_energy, ldos_density),
        ]
        for energy, values in spectra:
            if len(energy) != len(values):
                raise ValueError("Energy and intensity grids have different lengths")

        figure, axes = plt.subplots(2, 1, figsize=(7.0, 9.89), sharex=True)
        upper_axis = axes[0]
        lower_axis = axes[1]

        upper_axis.plot(ldos_energy, ldos_density, color="red", label="LDOS p")
        upper_axis.set_ylabel("LDOS [/eV]")
        upper_axis.set_ylim(bottom=0)
        upper_axis.legend(loc="lower right")

        lower_axis.plot(
            calculated_energy,
            calculated_absorption,
            color="black",
            label="XAS with broadening",
        )
        lower_axis.plot(raw_energy, raw_absorption, color="green", label="Raw XAS")
        lower_axis.plot(
            observed_energy,
            observed_absorption,
            color="blue",
            label="Experiment",
        )
        lower_axis.set_ylabel("Absorption [arb. unit]")
        lower_axis.set_xlabel("Photon energy [eV]")
        lower_axis.set_ylim(bottom=0)
        lower_axis.legend(loc="lower right")

        for axis in axes:
            axis.axvline(fermi_energy, color="black", linewidth=1)
            if xmin is not None or xmax is not None:
                axis.set_xlim(left=xmin, right=xmax)

        figure.tight_layout()
        return save_figure(figure, output)
