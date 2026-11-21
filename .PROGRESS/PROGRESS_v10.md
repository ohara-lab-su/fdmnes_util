# v10: pyproject.toml によるビルド設定への統一

- `setup.py` を削除しました。ビルド時の独自 `build_py` 処理は使用しません。
- `MANIFEST.in` を削除しました。
- `pyproject.toml` の `[tool.setuptools.data-files]` で `scripts/*.py` を配布します。サンプルの編集元は `scripts/` のみです。
- `fdmnes_util install script` は、インストール先の `share/fdmnes_util/scripts` からカレントディレクトリへコピーします。
- 同名ファイルは通常上書きせず、`--force` 指定時のみ置き換えます。
- 配置・コピー処理以外の計算アルゴリズムは変更していません。

## 確認結果

- `pytest tests/test_script_installer.py`: 4件成功
- `pip wheel --no-deps --no-build-isolation`: 成功
- wheel内の `share/fdmnes_util/scripts`: 14ファイル
- 仮想環境にwheelをインストールした後の `fdmnes_util install script`: 14件コピー
- 同じコマンドの再実行: 0件コピー、14件スキップ
