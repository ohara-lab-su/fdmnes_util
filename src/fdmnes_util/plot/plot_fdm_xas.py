#!/usr/bin/env python3
"""Plot XAS spectra. File parsing and energy conversion belong elsewhere."""

from . import _PlotFigure


class PlotFdmXas(_PlotFigure):
    """Matplotlib visualizations for FDMNES XAS."""

    def plot_convolved(self, eng, xas, output, *, specified=False):
        """SAE の fdXAS.py または fdXAS_specified.py の配置で描く。

        Args:
            eng: フェルミ準位を基準としたエネルギー。
            xas: 畳み込み後の吸収強度。
            output: 保存先のパス。
            specified: fdXAS_specified.py の目盛り・凡例を使う。

        Returns:
            保存した図のパス。
        """
        import matplotlib.pyplot as plt

        # SAE の設定をこの図に限定し、同じプロセスの別の描画へ波及させない。
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
            xsize = 0.75
            ysize = 0.83 / 2.0
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(eng, xas, linewidth=2, label="XAS")
            plt.xlabel("Energy above Fermi [eV]")
            plt.ylabel("Absorption [arb. unit]")
            if specified:
                plt.ticklabel_format(axis="x", useOffset=False)
                leg = plt.legend(fontsize=12, loc="lower right")
            else:
                plt.axvline(x=0, color="black", linewidth=1)
                leg = plt.legend(loc="lower right")
            leg.get_frame().set_alpha(0.5)
            return self._save_figure(figure, output, show=True)

    def plot(
        self,
        spectra,
        output,
        *,
        title=None,
        xlabel="Energy (eV)",
        ylabel="XAS",
        xmin=None,
        xmax=None,
        ymax=None,
        fermi_position=None,
    ):
        """Draw XAS curves on a common axis and save the figure.

        Args:
            spectra: Sequence of energy, intensity, and curve-label tuples.
            output: Destination path. The extension determines the figure format.
            title: Optional figure title.
            xlabel: Energy-axis label.
            ylabel: Absorption-axis label.
            xmin: Optional minimum energy.
            xmax: Optional maximum energy.
            ymax: Optional maximum absorption.
            fermi_position: Energy at which to draw the optional Fermi marker.

        Returns:
            pathlib.Path: Path to the saved figure.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axis = plt.subplots()
        for energy, intensity, label in spectra:
            axis.plot(energy, intensity, label=label)

        if fermi_position is not None:
            axis.axvline(fermi_position, color="black", linewidth=1)
        if xmin is not None or xmax is not None:
            axis.set_xlim(left=xmin, right=xmax)
        if ymax is not None:
            axis.set_ylim(top=ymax)
        axis.set_xlabel(xlabel)
        axis.set_ylabel(ylabel)
        axis.set_title(title)

        if any(label for _, _, label in spectra):
            axis.legend()

        figure.tight_layout()
        return self._save_figure(figure, output)

    def plot_sites(
        self,
        spectra,
        output,
        *,
        observed=None,
        xmin=None,
        xmax=None,
        ymax=None,
        fermi=False,
        fermi_position=None,
        extra_formats=False,
    ):
        """Draw computed and optionally observed XAS in separate panels.

        Args:
            spectra: Computed spectra as energy, intensity, label tuples.
            output: Destination path for the figure.
            observed: Optional Athena spectra for the upper panel.
            xmin: Optional lower limit of the energy axis.
            xmax: Optional upper limit of the energy axis.
            ymax: Optional upper limit of the absorption axis.
            fermi: Whether the energy axis is Fermi-relative.
            fermi_position: Energy of the vertical Fermi marker.
            extra_formats: Save the figure in EPS, PDF, and PNG.

        Returns:
            pathlib.Path: Destination of the saved figure.

        Raises:
            ValueError: If no calculated spectrum is supplied.
        """
        import matplotlib.pyplot as plt

        spectra = list(spectra)
        if not spectra:
            raise ValueError("No XAS spectra to plot")

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(8.1, 9.89))
            plt.subplot(2, 1, 2)
            for energy, intensity, label in spectra:
                plt.plot(energy, intensity, linewidth=1, label=label)
            plt.ticklabel_format(axis="x", useOffset=False)
            plt.ylabel("Absorption [arb. unit]")
            if fermi_position is not None:
                plt.axvline(x=fermi_position, color="black", linewidth=1)
            leg = plt.legend(loc="lower right")
            leg.get_frame().set_alpha(0.5)
            plt.xlim(xmax=xmax, xmin=xmin)
            plt.ylim(ymax=ymax)
            xas_xmin, xas_xmax = plt.xlim()
            if fermi:
                plt.xlabel("Energy above Fermi [eV]")
            else:
                plt.xlabel("Photon Energy [eV]")
            # Athena data plot
            if observed:
                plt.subplot(2, 1, 1)
                for energy, intensity, label in observed:
                    plt.plot(energy, intensity, label=label)
                plt.xlim([xas_xmin, xas_xmax])
                plt.ticklabel_format(axis="x", useOffset=False)
                leg = plt.legend(loc="lower right")
                leg.get_frame().set_alpha(0.5)
            return self._save_figure(figure, output, extra_formats=extra_formats, show=True)

    def plot_experiment_comparison(
        self,
        calculated_energy,
        calculated_absorption,
        observed_energy,
        observed_absorption,
        output,
        *,
        xmin=None,
        xmax=None,
        ymin=0.0,
        ymax=None,
    ):
        """Plot calculated and measured XAS on one photon-energy axis.

        The calculated energy must already be converted to photon energy.
        The caller is responsible for adding the FDMNES edge energy.

        Args:
            calculated_energy: Calculated photon energies in eV.
            calculated_absorption: Calculated absorption intensity.
            observed_energy: Experimental photon energies in eV.
            observed_absorption: Normalized experimental absorption.
            output: Destination PDF or image filename.
            xmin: Optional minimum photon energy in eV.
            xmax: Optional maximum photon energy in eV.
            ymin: Optional minimum absorption value.
            ymax: Optional maximum absorption value.

        Returns:
            pathlib.Path: Saved figure filename.
        """
        import matplotlib.pyplot as plt

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
            xsize = 0.75
            ysize = 0.83 / 2.0
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(
                calculated_energy,
                calculated_absorption,
                color="red",
                linewidth=1,
                label="FDM Green R3",
            )
            plt.plot(
                observed_energy,
                observed_absorption,
                color="blue",
                linewidth=1,
                label="exp.",
            )
            plt.xlabel("Photon Energy [eV]")
            plt.ylabel("Absorption [arb. unit]")
            leg = plt.legend(fontsize=12, loc="lower right")
            leg.get_frame().set_alpha(0.5)
            plt.xlim(xmax=xmax, xmin=xmin)
            plt.ylim(ymin=ymin, ymax=ymax)
            return self._save_figure(figure, output, show=True)

    def plot_composite(
        self,
        spectra,
        output,
        *,
        observed=None,
        dos=(),
        xlabel="Photon Energy [eV]",
        ylabel="Absorption [arb. unit]",
        xmin=None,
        xmax=None,
        ymax=None,
        dmax=None,
        fermi_position=None,
        extra_formats=False,
        show=False,
    ):
        """Draw SAE's experimental, calculated-XAS, and optional LDOS panels.

        Args:
            spectra: Calculated spectrum tuples of energy, intensity, and label.
            output: Main output filename.
            observed: Optional measured energy, absorption, and label tuple.
            dos: Optional LDOS tuples of energy, density, and label.
            xlabel: Label of the bottom energy axis.
            ylabel: Label of the calculated absorption axis.
            xmin: Lower common energy limit.
            xmax: Upper common energy limit.
            ymax: Upper calculated absorption limit.
            dmax: Upper LDOS limit.
            fermi_position: Optional Fermi marker on calculated panels, in eV.
            extra_formats: Also save EPS, PNG and PDF.
            show: Display the figure using the active Matplotlib backend.

        Returns:
            pathlib.Path: Main figure path.
        """
        import matplotlib.pyplot as plt

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(8.1, 9.89))
            rows = 2 + bool(dos)
            calculated = figure.add_subplot(rows, 1, 2)
            style = {"XAS broad": ("red", 3), "XAS": ("green", 1)}
            for energy, intensity, label in spectra:
                color, width = style.get(label.split(" (", 1)[0], ("green", 1))
                calculated.plot(
                    energy, intensity, label=label, color=color, linewidth=width
                )
            calculated.set_ylabel(ylabel)
            calculated.set_ylim(bottom=0, top=ymax)
            calculated.set_xlim(left=xmin, right=xmax)
            leg = calculated.legend(loc="lower right")
            leg.get_frame().set_alpha(0.5)

            axes = [calculated]
            bottom = calculated
            if observed is not None:
                observed_axis = figure.add_subplot(rows, 1, 1, sharex=calculated)
                energy, intensity, label = observed
                observed_axis.plot(energy, intensity, label=label)
                observed_axis.set_ylim(bottom=0)
                leg = observed_axis.legend(loc="lower right")
                leg.get_frame().set_alpha(0.5)
                axes.append(observed_axis)
            if dos:
                bottom = figure.add_subplot(rows, 1, 3, sharex=calculated)
                for energy, density, label in dos:
                    bottom.plot(energy, density, linewidth=1, label=label)
                bottom.set_ylabel("DOS [stat/eV]")
                bottom.set_ylim(bottom=0, top=dmax)
                leg = bottom.legend(loc="upper right")
                leg.get_frame().set_alpha(0.5)
                axes.append(bottom)
            if fermi_position is not None:
                calculated.axvline(fermi_position, color="black", linewidth=1)
                if dos:
                    bottom.axvline(fermi_position, color="black", linewidth=1)
            for axis in axes:
                axis.ticklabel_format(axis="x", useOffset=False)
            bottom.set_xlabel(xlabel)
            return self._save_figure(figure, output, extra_formats=extra_formats, show=show)
