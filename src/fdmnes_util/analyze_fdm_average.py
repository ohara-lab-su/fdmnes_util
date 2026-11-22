#!/usr/bin/env python3
"""``*_sdN.txt`` や ``*_conv.txt`` から読み込んだスペクトルを平均する。

AnalyzeFdmAverage はリーダーから数値配列を受け取り、格子が一致することを確認して平均する。必要なエネルギー基準は ``*.inp`` と生 XAS ``<Filout>.txt`` のリーダーから得る。ファイルの読み書きは呼び出し側が担当する。

SAE の ``sae/commands/fdPDOS_XAS_av.py`` から、三つの計算の平均処理を取り出した。
SAE 原版の日付は2015年9月9日で、2018年8月17日に Python 2/3 に対応した。
"""

import numpy as np


class AnalyzeFdmAverage:
    """``*_sdN.txt`` や ``*_conv.txt`` を読んだリーダーから値を取得して平均する。"""
    def energy_reference(self, input_file, spectrum, fermi=False):
        """SAE の平均図に使う共通のエネルギー移動量を決める。

        SAE 原版はフェルミ準位基準と光子エネルギー基準を区別する。光子エネルギーから変換する分岐では、原版で未代入だった差分を移動量として使う。

        Args:
            input_file: 計算条件とエネルギー基準を読む FdmInp。
            spectrum: 吸収端とフェルミエネルギーを保持する FdmTxt。
            fermi: True の場合はフェルミ準位基準、False の場合は光子エネルギー基準。

        Returns:
            tuple[float, float]: エネルギー軸の移動量と光子エネルギー基準のフェルミ準位。両方とも eV。

        Raises:
            ValueError: 必要なエネルギーのメタデータが非有限の場合。
        """
        edge_energy = float(spectrum.get_eedge())
        fermi_energy = float(spectrum.get_efermi())

        if not np.isfinite(edge_energy):
            raise ValueError("The absorption-edge energy must be finite")
        if not np.isfinite(fermi_energy):
            raise ValueError("The Fermi energy must be finite")

        absolute_fermi = edge_energy + fermi_energy
        photon_mode = input_file.get_energygpho()

        if photon_mode:
            if fermi:
                energy_shift = -absolute_fermi
            else:
                energy_shift = 0.0
        else:
            if fermi:
                energy_shift = -fermi_energy
            else:
                energy_shift = edge_energy

        return energy_shift, absolute_fermi

    def average(self, readers, value_method, *, divisor=None, **kwargs):
        """共通のエネルギー軸と指定データの算術平均を返す。

        Args:
            readers: FDMNES 出力のリーダーを一つ以上並べたもの。
            value_method: 各リーダーから値を取得するメソッド名。
            divisor: 原子あたりの規格化などで合計を割る正の値。省略時はリーダーの件数。
            **kwargs: 対象のメソッドに渡す追加のキーワード引数。

        Returns:
            tuple[numpy.ndarray, numpy.ndarray]: エネルギー軸と平均値。

        Raises:
            ValueError: リーダーが空、格子が異なる、または数値が非有限か配列の次元が不一致の場合。
            AttributeError: 指定の取得メソッドがない場合。
        """
        if not readers:
            raise ValueError("At least one calculation is required")
        if divisor is None:
            divisor = len(readers)
        if not np.isfinite(divisor) or divisor <= 0:
            raise ValueError("The averaging divisor must be positive and finite")

        reference_energy = None
        sum_values = None

        for reader in readers:
            energy = np.asarray(reader.get_eng(), dtype=float)
            if energy.ndim != 1:
                raise ValueError("Energy grid must be one-dimensional")
            if energy.size == 0 and reference_energy is None:
                raise ValueError("Energy grid must not be empty")
            if not np.all(np.isfinite(energy)):
                raise ValueError("Energy grid contains non-finite values")
            # 最初の計算を基準にし、各計算のエネルギー軸を一度だけ取得する。
            if reference_energy is None:
                reference_energy = energy
            elif energy.shape != reference_energy.shape:
                raise ValueError("Energy grid lengths differ between calculations")
            elif not np.allclose(energy, reference_energy, rtol=0.0, atol=1e-8):
                raise ValueError("Energy grids differ between calculations")

            accessor = getattr(reader, value_method)
            values = np.asarray(accessor(**kwargs), dtype=float)
            if values.ndim == 0:
                raise ValueError("Spectrum values must have an energy dimension")
            if not np.all(np.isfinite(values)):
                raise ValueError("Spectrum contains non-finite values")
            if values.shape[0] != reference_energy.shape[0]:
                raise ValueError("Energy and data lengths differ")

            if sum_values is None:
                sum_values = np.zeros_like(values, dtype=float)
            if values.shape != sum_values.shape:
                raise ValueError("Data shapes differ between calculations")
            sum_values += values

        mean_values = sum_values / divisor
        return reference_energy.copy(), mean_values
