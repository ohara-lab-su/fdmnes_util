#!/usr/bin/env python3
# SAE provenance: sae/commands/FDxyz2fdm.py.
# Original author: Kengo NAKADA; Copyright 2015, Kengo NAKADA; MIT.
# Original development history (verbatim):
# 2018.08.21
#  Python2/3 両対応
# 2015.06.30
#  == None --> is None
# 2015.05.18 startup
# SAE source for XYZ output: sae/commands/FDbav2xyz.py.
# 2015.06.24 startup
# 2018.08.21 Python2/3 両対応
"""BAV からの構造書き出しや FDMNES 入力の作成に使う標準 ``*.xyz`` を読み書きする。

Xyz は原子数、元素記号、Å 単位の直交座標を扱う。座標だけから FDMNES の構造節を作る処理は FdmStructure が担当する。

SAE の変換では ReadMd と AseInputOperations を使用していた。このモジュールの対象は標準 XYZ。
"""

from pathlib import Path


class Xyz:
    """構造入出力の `*.xyz` を扱い、元素記号と直交座標を読み書きする。"""

    def __init__(self, filename: str | Path) -> None:
        """XYZ ファイルを読み込む。

        Args:
            filename: 対象ファイルのパス。

        Raises:
            ValueError: 原子数または座標の記録が不正な場合。
        """
        self.filename = Path(filename)
        self.symbols: list[str] = []
        self.positions: list[tuple[float, float, float]] = []
        self.read()

    def read(self) -> None:
        """原子数と各原子の直交座標の行を解釈する。

        Raises:
            ValueError: 入力が正しい標準 XYZ ではない場合。
        """
        lines = self.filename.read_text(encoding="utf-8").splitlines()
        if len(lines) < 2:
            raise ValueError("XYZ input must contain a count and a comment line")

        try:
            atom_count = int(lines[0].strip())
        except ValueError as error:
            raise ValueError("Invalid XYZ atom count") from error

        if atom_count < 0:
            raise ValueError("XYZ atom count cannot be negative")
        if len(lines) < atom_count + 2:
            raise ValueError("XYZ file contains fewer atoms than declared")

        symbols: list[str] = []
        positions: list[tuple[float, float, float]] = []
        for index in range(atom_count):
            fields = lines[index + 2].split()
            if len(fields) < 4:
                raise ValueError(f"Invalid XYZ coordinate at atom {index + 1}")
            symbol = fields[0]
            try:
                coordinates = (
                    float(fields[1]),
                    float(fields[2]),
                    float(fields[3]),
                )
            except ValueError as error:
                raise ValueError(
                    f"Invalid XYZ coordinate at atom {index + 1}"
                ) from error
            symbols.append(symbol)
            positions.append(coordinates)

        self.symbols = symbols
        self.positions = positions

    @staticmethod
    def render(symbols, positions) -> str:
        """FDbav2xyz が使う精度で直交座標をテキスト化する。

        先頭行に原子数、その次に空のコメント行、以降に元素と座標を1原子につき1行ずつ書く。

        Args:
            symbols: 原子順の元素記号。
            positions: Å 単位の原子座標。各行が1原子の3成分。

        Returns:
            末尾の改行まで含めた XYZ 本文。

        Raises:
            ValueError: 元素記号と原子位置の件数が異なるか、座標が3成分でない場合。
        """
        atom_symbols = list(symbols)
        atom_positions = list(positions)

        if len(atom_symbols) != len(atom_positions):
            raise ValueError("Atom/coordinate count mismatch")

        lines = [str(len(atom_symbols)), ""]

        for symbol, position in zip(atom_symbols, atom_positions):
            if len(position) != 3:
                raise ValueError("Each atom must have three coordinates")

            x_coordinate = float(position[0])
            y_coordinate = float(position[1])
            z_coordinate = float(position[2])

            # Preserve the ten-decimal-place coordinate representation.
            atom_line = (
                f" {symbol} {x_coordinate:14.10f} "
                f"{y_coordinate:14.10f} {z_coordinate:14.10f}"
            )
            lines.append(atom_line)

        return "\n".join(lines) + "\n"

    @classmethod
    def write(cls, symbols, positions, filename) -> Path:
        """指定した原子座標を XYZ ファイルに保存する。

        Args:
            symbols: 原子順の元素記号。
            positions: Å 単位の原子座標。各行が1原子の3成分。
            filename: 対象ファイルのパス。

        Returns:
            保存したファイルのパス。

        Raises:
            ValueError: 元素記号と原子位置の対応が不正な場合。
            OSError: 保存先に書き込めない場合。
        """
        output_path = Path(filename)
        output_path.write_text(cls.render(symbols, positions), encoding="utf-8")
        return output_path
