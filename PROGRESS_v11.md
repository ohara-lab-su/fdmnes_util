# rebuild v11 — 可読性規約の適用（途中成果）

## プロジェクト共通の開発規約

- PEP 8 を基本に、Black の標準的なレイアウトに従う。
- 三項演算子（`x if condition else y`）を使用しない。
- `if`、`else`、`try`、`except` 等の本体を同一行に書かない。
- 複数の処理をセミコロンで結合しない。内包表記も可読性を優先する。
- 全Pythonファイルにシバンを付け、Googleスタイルのdocstringと必要なコメントを書く。
- Pythonクラス名はCapWords、モジュール名はsnake_caseに対応させる。
- Pythonのパッケージ設定・ビルド・配布は `pyproject.toml` を用い、`setup.py` を置かない。
- 既存仕様とアルゴリズムは原本に照らして維持し、未確認の挙動を補わない。

## 今回のソース変更

- `read_fdm_bav_2016.py` と `read_fdm_bav_2020.py`: 省略した条件・例外処理・三項演算子・一行メソッドを展開し、Googleスタイルのdocstringを追加。
- `read_fdm_bav.py`: 年度判定を明示的な処理に変更。
- `read_fdm_sd_2016.py`: 2016年形式の列順序と積分DOS計算を維持しつつ、省略表記を展開。
- `read_fdmfile.py`: 読み込みと例外処理を展開。
- プロットクラスは既存の `plot/`、編集可能なサンプルは `scripts/` に維持。
- `fdmnes_util install script` および `pyproject.toml` からの同梱方式を維持。

## 確認

- `PYTHONPATH=src pytest -q`: **33 passed**
- Black は環境にインストールされていないため、Blackコマンドの実行結果はありません。
- なお、上記以外の既存ファイルには一行処理やdocstring不足が残っています。全面的なスタイル準拠は未完了です。
- SAEの28本のスクリプトの機能再現も未完了です。
