#!/usr/bin/env python3
"""``<Filout>.txt``、``*_conv.txt``、``*.nor`` などから読んだスペクトルの数値配列を図にする。

PlotFdmXas は計算・実測 XAS の重ね描きやパネル配置を担当し、指定された ``*.pdf`` などの図を保存する。
"""
from . import _PlotFigure


class PlotFdmXas(_PlotFigure):
    """``<Filout>.txt``・``*_conv.txt``・``*.nor`` などから取得した XAS の数値配列を受け取り、図を保存する。"""
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
        """共通軸に XAS を描いて保存する。

        Args:
            spectra: エネルギー、強度、曲線ラベルの組の並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            title: 省略可能な図のタイトル。
            xlabel: エネルギー軸のラベル。
            ylabel: 吸収強度軸のラベル。
            xmin: 省略可能な横軸の下限。
            xmax: 省略可能な横軸の上限。
            ymax: 省略可能な吸収強度の上限。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。

        Returns:
            pathlib.Path: 保存したファイルのパス。
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
        """計算 XAS と任意の実測 XAS を別々のパネルに描く。

        Args:
            spectra: 計算スペクトルのエネルギー、強度、ラベルの並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            observed: 任意の実測吸収スペクトル。
            xmin: 省略可能な横軸の下限。
            xmax: 省略可能な横軸の上限。
            ymax: 省略可能な吸収強度の上限。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            extra_formats: 同じ図を PDF・EPS・PNG でも保存する指定。

        Returns:
            pathlib.Path: 図の保存先。

        Raises:
            ValueError: 計算スペクトルが空の場合。
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
        """計算と実測の XAS を同じ光子エネルギー軸上に描く。

        計算値には、呼び出し側で吸収端エネルギーを加えて光子エネルギーに換算した軸を渡す。

        Args:
            calculated_energy: 計算の光子エネルギー（eV）。
            calculated_absorption: 計算の吸収強度。
            observed_energy: 実測の光子エネルギー（eV）。
            observed_absorption: 実測の吸収強度。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            xmin: 省略可能な横軸の下限。
            xmax: 省略可能な横軸の上限。
            ymin: 省略可能な吸収強度の下限。
            ymax: 省略可能な吸収強度の上限。

        Returns:
            pathlib.Path: 保存したファイルのパス。
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
        """SAE の実測・計算 XAS と任意の LDOS パネルを描く。

        Args:
            spectra: 計算スペクトルのエネルギー、強度、ラベルの並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            observed: 任意の実測吸収スペクトル。
            dos: 任意の LDOS のエネルギー、密度、ラベルの組。
            xlabel: エネルギー軸のラベル。
            ylabel: 吸収強度軸のラベル。
            xmin: 省略可能な横軸の下限。
            xmax: 省略可能な横軸の上限。
            ymax: 省略可能な吸収強度の上限。
            dmax: 省略可能な状態密度の上限。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            extra_formats: 同じ図を PDF・EPS・PNG でも保存する指定。
            show: 保存後に描画バックエンドで図を表示する指定。

        Returns:
            pathlib.Path: 保存したファイルのパス。
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
