"""FDMNES の2026年版で確認した複素射影・f 軌道付きの ``*_sdN.txt`` を読む。

FdmSd2026 は列見出しから基底、スピン数、最大角運動量を判定する。エネルギー、状態密度、積分値の対応は元の列順を保つ。
"""
from pathlib import Path

import numpy as np

from .fdm_sd_2020 import FdmSd2020


class FdmSd2026:
    """FDMNES の出力 `*_sdN.txt` を2026年形式で読み、複素射影や f 軌道の密度を取得する。"""
    _GROUPS = ("s", "p", "d", "f")
    _REAL_F = ("fxyz", "fx3", "fy3", "fz3", "fx(y2-z2)", "fy(z2-x2)", "fz(x2-y2)")
    _TESSERAL_F = ("(3,-3)", "fxyz", "(3,-1)", "fz3", "(3,1)", "fz(x2-y2)", "(3,3)")
    ORBITALS = FdmSd2020.ORBITALS
    ALIASES = FdmSd2020.ALIASES
    total_ispin = FdmSd2020.total_ispin

    def __init__(self, filename, *, weight=None):
        """列名から軌道・基底・スピンを判定し、SD を読み込む。"""
        self.path = Path(filename)
        lines = self.path.read_text(errors="replace").splitlines()
        if len(lines) < 2:
            raise ValueError("Incomplete SD file")

        self.columns = lines[0].split()
        self._complex = "(0,0)" in self.columns or "(1,0)_up" in self.columns
        self._tesseral = not self._complex and (
            "(3,-3)" in self.columns or "(3,-3)_up" in self.columns
        )
        self.ispin, self.lmax = self._layout(self.columns)
        self.values = np.loadtxt(lines[1:], ndmin=2)
        required = self._required_columns(self.ispin, self.lmax)
        if len(self.values) == 0 or self.values.shape[1] != len(self.columns):
            raise ValueError("SD column count mismatch or missing data")
        if required != set(self.columns) or len(self.columns) != len(required):
            missing = sorted(required.difference(self.columns))
            raise ValueError(f"Invalid extended SD columns; missing: {missing}")
        self._fields = dict(zip(self.columns, self.values.T))

        if weight is not None:
            divisor = float(weight)
            if divisor == 0:
                raise ValueError("weight must be nonzero")
            # Energy は除く
            for name, column in self._fields.items():
                if name != "Energy":
                    column /= divisor
        self.energy = self._fields["Energy"].copy()

    @staticmethod
    def _matches_header(columns):
        """複素射影または f 軌道の積分列があるかを判定する。"""
        return any(
            name in columns for name in ("(0,0)", "(1,0)_up", "Int(f)", "Int(f)_up")
        )

    def _layout(self, columns):
        """積分列の見出しからスピン数と最大角運動量を決める。"""
        spin = 1
        if "s_up" in columns:
            spin = 2
        for level in range(3, -1, -1):
            group = self._GROUPS[level]
            if f"Int({group})" in columns or f"Int({group})_up" in columns:
                return spin, level
        raise ValueError("SD header has no orbital integral columns")

    def _required_columns(self, ispin, lmax):
        """基底・スピン数・最大角運動量に対応する必須列を列挙する。"""
        names = set()
        for level in range(lmax + 1):
            group = self._GROUPS[level]
            names.update((group, f"Int({group})"))
            if self._complex and level != 0:
                names.update(f"({level},{m})" for m in range(-level, level + 1))
        if not self._complex:
            names.update(name for name, (l, _) in self.ORBITALS.items() if l <= lmax)
            if lmax == 3:
                if self._tesseral:
                    names.update(self._TESSERAL_F)
                else:
                    names.update(self._REAL_F)
        if self._complex and ispin == 1:
            names.remove("s")
            names.add("(0,0)")
        if ispin == 2:
            names = {f"{name}_{spin}" for name in names for spin in ("up", "dn")}
        names.update(("Energy", "total", "Int(total)"))
        return names

    def get_densities(self):
        """密度と積分の列をファイルの順番で返す。"""
        if self.columns[0] == "Energy":
            return self.values[:, 1:]
        return np.delete(self.values, self.columns.index("Energy"), axis=1)

    def get_eng(self):
        """エネルギー軸を eV 単位で返す。"""
        return self.energy

    def get_lmax(self):
        """利用可能な最大軌道角運動量を返す。"""
        return self.lmax

    def get_ispin(self):
        """スピン数を返す。"""
        return self.ispin

    def _spin_suffix(self, spin):
        """実ファイルの軌道列に付くスピンの接尾辞を返す。"""
        if spin in (0, "up", "non", "nonmag"):
            if self.ispin == 1:
                return ""
            return "_up"
        if self.ispin == 1:
            raise ValueError("This SD file has one spin channel")
        if spin in (1, "dn", "down"):
            return "_dn"
        raise ValueError(f"Unknown SD spin channel: {spin}")

    def get_ldos(self, l=0, spin=0):
        """指定軌道群の状態密度を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: 指定した軌道の状態密度。

        Raises:
            ValueError: 指定されたスピン列がない場合。
            IndexError: 数値で指定した角運動量が範囲外の場合。
            KeyError: 対象の軌道列が存在しない場合。
        """
        suffix = self._spin_suffix(spin)
        if self._complex and self.ispin == 1 and l in (0, "s"):
            return self._fields["(0,0)"]
        if isinstance(l, int):
            key = self._GROUPS[l]
        else:
            key = l
        return self._fields[f"{key}{suffix}"]

    def get_intldos(self, l=0, spin=0):
        """指定した角運動量の状態密度の積分値を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: ファイルのエネルギー格子に対応する積分状態密度。

        Raises:
            ValueError: 指定されたスピン列がない場合。
            IndexError: 数値で指定した角運動量が範囲外の場合。
            KeyError: 対象の軌道の積分列が存在しない場合。
        """
        suffix = self._spin_suffix(spin)
        if isinstance(l, int):
            key = self._GROUPS[l]
        else:
            key = l
        return self._fields[f"Int({key}){suffix}"]

    def _get_real_pdos(self, l=0, m=0, lm=None, spin=0):
        """角運動量量子数 l と磁気量子数 m で指定した軌道の射影状態密度を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            m: 磁気量子数。
            lm: l と m に優先して指定する軌道名。省略可能。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: 射影状態密度の配列。

        Raises:
            KeyError: 対象の軌道列が存在しない場合。
            ValueError: 指定されたスピン列がない場合。
        """
        suffix = self._spin_suffix(spin)
        if lm is not None:
            orbital_name = lm.lower()
            key = self.ALIASES.get(orbital_name, orbital_name)
        else:
            key = None
            for orbital_name, quantum_numbers in self.ORBITALS.items():
                if quantum_numbers == (l, m):
                    key = orbital_name
                    break

        if key not in self.ORBITALS:
            raise KeyError(f"Orbital absent: {key}")
        return self._fields[f"{key}{suffix}"]

    def get_tdos(self, spin=0):
        """FDMNES が出力した全状態密度の列を返す。

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: 各エネルギー点につき一つの値。

        Raises:
            ValueError: 指定されたスピン列がない場合。
        """
        self._spin_suffix(spin)
        return self._fields["total"]

    def get_inttdos(self, spin=0):
        """FDMNES が出力した全状態密度の積分列を返す。

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: 各エネルギー点につき一つの値。

        Raises:
            ValueError: 指定されたスピン列がない場合。
        """
        self._spin_suffix(spin)
        return self._fields["Int(total)"]

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """射影密度を返す。実 f 射影はファイルの列名を lm に指定する。"""
        suffix = self._spin_suffix(spin)
        fields = self._fields
        if lm is not None:
            name = lm.lower()
            if name in self._REAL_F or (self._tesseral and name in self._TESSERAL_F):
                return fields[f"{name}{suffix}"]
            if self._complex:
                name = self.ALIASES.get(name, name)
                if name in ("s", "(0,0)"):
                    return self.get_ldos(l=0, spin=spin)
                if name.startswith("("):
                    return fields[f"{name}{suffix}"]
                raise KeyError("Use l and m for projections in the complex basis")
        if self._complex:
            if l == 0 and m == 0:
                return self.get_ldos(l=0, spin=spin)
            return fields[f"({l},{m}){suffix}"]
        if l == 3 and lm is None and self._tesseral and -3 <= m <= 3:
            return fields[f"{self._TESSERAL_F[m + 3]}{suffix}"]
        return self._get_real_pdos(l=l, m=m, lm=lm, spin=spin)
