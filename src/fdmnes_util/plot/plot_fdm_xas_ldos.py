#!/usr/bin/env python3
"""Plot XAS and site-resolved LDOS as a vertically stacked figure."""

from . import _PlotFigure


class PlotFdmXasLdos(_PlotFigure):
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
        import matplotlib.pyplot as plt

        series = list(orbital_spectra)
        if not series:
            raise ValueError("At least one orbital spectrum is required")

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            off = 0.01
            xsize = 0.75
            ysize0 = 0.83
            norbit = len(series)
            ysize = ysize0 / (norbit + 1)
            num = 0
            plt.axes([orgx, orgy, xsize, ysize])
            engx, xas = xas
            label = "XAS"
            color = plt.cm.prism(float(num + 1) / float(norbit))
            plt.plot(engx, xas, linewidth=2, color=color, label=label)
            if fermi_position is not None:
                plt.axvline(x=fermi_position, color="black", linewidth=1)
            plt.ylim(ymin=0)
            leg = plt.legend(loc="lower right")
            leg.get_frame().set_alpha(0.5)
            if fermi:
                plt.xlabel("Energy above Fermi [eV]")
            else:
                plt.xlabel("Photon Energy [eV]")
            plt.ylabel("Absorption [arb. unit]")
            orgy = orgy + ysize + off
            for label, eng, dos in series:
                plt.axes([orgx, orgy, xsize, ysize])
                num += 1
                color = plt.cm.prism((num + 1) * 10)
                plt.plot(eng, dos, linewidth=2, color=color, label=label)
                if fermi_position is not None:
                    plt.axvline(x=fermi_position, color="black", linewidth=1)
                plt.ylim(ymin=0)
                plt.xticks([])
                leg = plt.legend(loc="upper right")
                leg.get_frame().set_alpha(0.5)
                orgy = orgy + ysize + off
            return self._save_figure(figure, output, show=True)

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

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            off = 0.01
            xsize = 0.75
            ysize = 0.83 / 2.0
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(
                calculated_energy,
                calculated_absorption,
                color="black",
                linewidth=3,
                label="XAS with Broad",
            )
            plt.plot(
                raw_energy,
                raw_absorption,
                color="green",
                linewidth=1,
                label="XAS raw data",
            )
            plt.plot(
                observed_energy,
                observed_absorption,
                color="blue",
                linewidth=3,
                label="exp. BL14B2",
            )
            plt.axvline(x=fermi_energy, color="black", linewidth=1)
            plt.yticks([])
            plt.xlim(xmax=xmax, xmin=xmin)
            plt.ylim(ymin=0)
            plt.xlabel("Photon Energy [eV]")
            plt.ylabel("Absorption [arb. unit]")
            leg = plt.legend(fontsize=12, loc="lower right")
            leg.get_frame().set_alpha(0.5)
            orgy = orgy + ysize + off
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(ldos_energy, ldos_density, color="red", linewidth=2, label="LDOS Cu-p")
            plt.axvline(x=fermi_energy, color="black", linewidth=1)
            plt.xticks([])
            plt.xlim(xmax=xmax, xmin=xmin)
            plt.ylim(ymin=0)
            plt.ylabel("LDOS [/eV]")
            leg = plt.legend(fontsize=12, loc="lower right")
            leg.get_frame().set_alpha(0.5)
            return self._save_figure(figure, output, show=True)
