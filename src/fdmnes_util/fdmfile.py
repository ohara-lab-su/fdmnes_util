#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/fdmfile.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *.txt ファイル
#
###############################################################################
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.11.12 startup
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import optparse
# import numpy as np
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
###############################################################################
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
# SAE source: sae/fdmnes/fdmfile_writer.py
# ---- SAE original header ----
# coding:utf-8
# 固定
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""FDMNES が起動時に読むジョブ一覧 ``fdmfile.txt`` を読み書きする。

Fdmfile は件数と順序付きの ``*.inp`` パスを保持する。単一入力の選択では明示したパスを優先し、指定がなければ一覧の先頭または ``read_pdb.inp`` を使う。
"""
from pathlib import Path


class Fdmfile:
    """FDMNES が起動時に読む ``fdmfile.txt`` を読み書きし、実行順の計算入力パスを保持する。"""
    def __init__(self, filename="fdmfile.txt"):
        """ジョブ一覧を読み込む。

        Args:
            filename: FDMNES のジョブ一覧のパス。

        Raises:
            ValueError: ジョブ一覧が空または不完全な場合。
        """
        self.path = Path(filename)
        lines = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            # FDMNES batch lists can start with a descriptive comment block.
            stripped = line.partition("!")[0].strip()
            if stripped:
                lines.append(stripped)
        if not lines:
            raise ValueError("Empty fdmfile.txt")
        count = int(lines[0])
        if count < 0:
            raise ValueError("Negative FDMNES job count")
        self.filenames = lines[1 : 1 + count]
        if len(self.filenames) != count:
            raise ValueError("Incomplete fdmfile.txt")

    def get_filout(self) -> str:
        """最初のジョブのファイル名を返す。ジョブがなければ空文字列。"""
        if self.filenames:
            return self.filenames[0]
        return ""

    @classmethod
    def select_input(cls, filename: str | Path | None = None) -> Path:
        """現在の作業フォルダから計算入力を選ぶ。

        Args:
            filename: 計算入力の明示指定。省略時は fdmfile.txt の先頭ジョブ、なければ read_pdb.inp。

        Returns:
            選択した計算入力のパス。

        Raises:
            ValueError: ジョブ一覧が不正またはジョブがない場合。
            FileNotFoundError: 選択した入力がファイルでない場合。
        """
        if filename is not None:
            path = Path(filename)
        elif Path("fdmfile.txt").is_file():
            first_input = cls().get_filout()
            if not first_input:
                raise ValueError("fdmfile.txt contains no calculation inputs")
            path = Path(first_input)
        else:
            path = Path("read_pdb.inp")

        if not path.is_file():
            raise FileNotFoundError(f"FDMNES input file not found: {path}")
        return path

    @staticmethod
    def write(filenames, filename="fdmfile.txt"):
        """ジョブ総数と各入力ファイル名を書き出す。

        Args:
            filenames: 計算入力のファイル名を実行順に並べたもの。
            filename: 対象ファイルのパス。

        Returns:
            Path: 保存したファイルのパス。
        """
        input_names = list(filenames)
        output_path = Path(filename)
        ncal = len(input_names)
        # FDmakeCconvAllsite.py の fdmfile.txt 出力。
        with output_path.open("w", encoding="utf-8") as fdmlist:
            print("", file=fdmlist)
            print(" " + str(ncal), file=fdmlist)
            for input_name in input_names:
                print(input_name, file=fdmlist)
        return output_path
