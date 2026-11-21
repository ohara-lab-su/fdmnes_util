# Rebuild v13

- `src/fdmnes_util/read_vasp_poscar.py`: 外部 `vasp_util.vasp_poscar.VaspPoscar` の公開APIから格子・分数座標・原子種を取得する。VASPパーサーの複製はしない。
- `src/fdmnes_util/write_fdm_structure.py`: FDMNESのCrystal/Molecule構造部分の書き出し。
- `scripts/FDvasp2fdm.py`: 編集可能なサンプルを追加。`fdmnes_util install script` の配布対象。
- `tests/test_vasp_module_bridge.py`: 外部モジュール呼び出しとFDMNES構造出力をテスト。

未完了: SAE原本の `FDvasp2fdm.py` が出力する計算条件付き `.inp` のひな形。FDMNES→POSCAR書き出しは `vasp_util` の公開API確認後に接続する。2016/2020/2022のSD・BAV実データ照合と28本のスクリプト再現も継続。

確認: 全テスト37件成功。`vasp-util` の配布名は提供された `src.zip` の `PKG-INFO` で確認した。
