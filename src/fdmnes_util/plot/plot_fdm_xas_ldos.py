#!/usr/bin/env python3
"""``<Filout>.txt``、``*_conv.txt``、``*_sdN.txt`` などに由来する XAS と LDOS の数値配列を図にする。

PlotFdmXasLdos は独立したエネルギー格子を保持して上下のパネルに描き、指定された ``*.pdf`` などに保存する。
"""
from . import _PlotFigure


class PlotFdmXasLdos(_PlotFigure):
    """``<Filout>.txt``・``*_conv.txt``・``*_sdN.txt`` に由来する数値配列を使い、XAS と LDOS の図を保存する。"""
    def plot(self, xas, orbital_spectra, output, *, fermi_position=None, fermi=False):
        """XAS と軌道別 LDOS を並べた図を保存する。

        Args:
            xas: エネルギーと吸収強度の配列の組。
            orbital_spectra: 軌道名、エネルギー、LDOS の組の並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: 軌道スペクトルが空の場合。
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
        """SAE の計算・実験 XAS と LDOS を二段で比較する。

        上段は p-LDOS、下段は畳み込み XAS、生 XAS、Athena の測定値。各スペクトルはそれぞれの格子を使う。

        Args:
            calculated_energy: 計算の光子エネルギー（eV）。
            calculated_absorption: 計算の吸収強度。
            raw_energy: 生 XAS の光子エネルギー。
            raw_absorption: 生 XAS の吸収強度。
            observed_energy: 実測の光子エネルギー（eV）。
            observed_absorption: 実測の吸収強度。
            ldos_energy: LDOS 格子に対応する光子エネルギー。
            ldos_density: p 軌道の LDOS。
            fermi_energy: エネルギー軸の基準に対応するフェルミエネルギー（eV）。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            xmin: 省略可能な横軸の下限。
            xmax: 省略可能な横軸の上限。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: スペクトルのエネルギー軸と強度配列の長さが異なる場合。
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
