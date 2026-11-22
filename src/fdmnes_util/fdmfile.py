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
"""Read and write the FDMNES batch list of calculation inputs."""

from pathlib import Path


class Fdmfile:
    """Represent the ordered input filenames in an FDMNES batch list."""

    def __init__(self, filename="fdmfile.txt"):
        """Load the batch list.

        Args:
            filename: Path to ``fdmfile.txt``.

        Raises:
            ValueError: If the list is empty or incomplete.
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
        """Return the filename of the first job, or an empty string."""
        if self.filenames:
            return self.filenames[0]
        return ""

    @classmethod
    def select_input(cls, filename: str | Path | None = None) -> Path:
        """Select a calculation input in the current working directory.

        Args:
            filename: Explicit calculation input. If omitted, use the first
                job in ``fdmfile.txt`` or default to ``read_pdb.inp``.

        Returns:
            The selected calculation input path.

        Raises:
            ValueError: If the batch list is invalid or contains no jobs.
            FileNotFoundError: If the selected input is not a file.
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
        """Write the job count and each input filename.

        Args:
            filenames: Iterable of FDMNES input filenames.
            filename: Destination path for the job-list file.

        Returns:
            Path: Path of the generated job-list file.
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
