#!/usr/bin/env python3
"""``<Filout>.txt``、``*_bav.txt``、``*_conv.txt``、``*_sdN.txt`` と補助ログを管理する。

FdmResultFiles は Filout からファイルのパスを探し、整理・移動・削除する。スペクトルやログの本文は読み込まない。
"""
import shutil
from glob import escape
from pathlib import Path


class FdmResultFiles:
    """``<Filout>.txt``、``*_bav.txt``、``*_conv.txt``、``*_sdN.txt`` と補助ログのパスを管理する。"""
    def __init__(self, filout: str | Path) -> None:
        """計算出力の接頭辞を保持する。

        Args:
            filout: ディレクトリを含められる出力ファイルの接頭辞。

        Raises:
            ValueError: 接頭辞にファイル名の部分がない場合。
        """
        self.filout = Path(filout)
        if not self.filout.name or self.filout.name == "..":
            raise ValueError("Empty or invalid Filout prefix")

    def outputs(self) -> list[Path]:
        """存在する計算出力と補助ファイルを返す。"""
        paths = self.move_outputs()
        # Callers may select a run outside the current working directory.
        for name in ("fdmnes_error.txt", "fdm.out", "PBS_log"):
            path = self.filout.parent / name
            if path.is_file() and path not in paths:
                paths.append(path)
        return paths

    def move_outputs(self) -> list[Path]:
        """存在する生 XAS、BAV、畳み込み XAS、SD を返す。"""
        folder = self.filout.parent
        stem = self.filout.name
        candidates = []
        for suffix in (".txt", "_bav.txt", "_conv.txt"):
            candidates.append(folder / f"{stem}{suffix}")

        # Filout is literal. Only the site suffix can match a pattern.
        candidates.extend(sorted(folder.glob(f"{escape(stem)}_sd*.txt")))
        return [path for path in candidates if path.is_file()]

    def clean(self) -> list[Path]:
        """結果と補助ファイルを削除し、そのパスを返す。"""
        deleted = []
        for path in self.outputs():
            path.unlink(missing_ok=True)
            deleted.append(path)
        return deleted

    def move(self, destination: str | Path) -> list[Path]:
        """計算結果を元のファイル名で保存先へ移動する。

        Args:
            destination: 保存先のパス。

        Returns:
            移動したファイルの保存先パス。
        """
        folder = Path(destination)
        folder.mkdir(parents=True, exist_ok=True)
        moved = []
        for path in self.move_outputs():
            target = folder / path.name
            moved_path = shutil.move(str(path), str(target))
            moved.append(Path(moved_path))
        return moved

    def rename(self, destination: str | Path) -> list[Path]:
        """SAE の FDmove と同じように、出力を新しい `Filout` 接頭辞へ移動する。

        Args:
            destination: 保存先のパス。

        Returns:
            計算結果順の移動先パス。

        Raises:
            FileExistsError: 移動先にファイルが既にある場合。
            OSError: ファイルを移動できない場合。
            ValueError: 移動先にファイル名の部分がない場合。
        """
        prefix = Path(destination)
        if not prefix.name or prefix.name == "..":
            raise ValueError("Destination must include a filename prefix")

        pairs = []
        for source in self.move_outputs():
            suffix = source.name[len(self.filout.name) :]
            target = prefix.with_name(prefix.name + suffix)
            if source.resolve() == target.resolve() and not target.is_symlink():
                continue
            if target.exists() or target.is_symlink():
                raise FileExistsError(f"Destination already exists: {target}")
            pairs.append((source, target))

        moved = []
        for source, target in pairs:
            source.rename(target)
            moved.append(target)
        return moved
