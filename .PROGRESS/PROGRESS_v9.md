# rebuild v9 — 編集可能なサンプルスクリプトの配布

- 旧 `src/fdmnes_util/commands/` を廃止し、対応済み14本をリポジトリ直下の `scripts/` に移動。
- `fdmnes_util install script` を実装。カレントディレクトリへコピーし、同名ファイルは原則上書きしない。`--force` と `--directory` をサポート。
- エントリーポイントをパッケージ管理コマンド1本に統一。サンプルスクリプト自身はCLIエントリーポイントに登録しない。
- `setup.py` の `build_py` で `scripts/` をホイールの `_script_examples/` に同梱。編集元は `scripts/` のみ。
- README.ja.md と README.md にインストール・編集方法を追記。
- 既存テストをサンプルスクリプト読み込み方式へ変更し、インストーラ回帰テストを追加。
- FDclean.py・FDplot_XAS.py・FDplot_LDOS.py・FDplot_PDOS.py は可読性優先で整理。

未完成: 28本すべての機能再現、既存14本の全オプション照合、2016/2022出力の網羅的検証。
