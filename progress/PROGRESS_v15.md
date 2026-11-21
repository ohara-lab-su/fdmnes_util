# v15 — 全Pythonファイルの記述規則の監査と修正

v14を基準に、パッケージ、サンプル、テストの全PythonファイルをASTで調査しました。

- 一行if文7箇所を通常の複数行if文へ展開しました。
- docstringが存在しなかったクラス・関数50箇所に、Googleスタイルの基本的なdocstringを追加しました。ただし一部は機械的な説明文であり、引数の意味・戻り値・例外の精査は**未完了**です。
- セミコロンによる複数文の連結10箇所を分離しました。
- 三項演算子はAST監査で0箇所です。
- ASTでのdocstring未記載、同一行ifは0箇所です。
- `PYTHONPATH=src pytest -q --disable-warnings`: **39 passed**。

## 重要な未完了事項

Blackはこの環境に存在しないため、Blackによる整形は実施していません。PEP 8の全項目への準拠も保証しません。特に演算子の前後の空白、長い行、Googleスタイルのdocstringの説明の質、過度に簡略化された既存処理には追加修正が必要です。

ライブラリの機能・計算式・2016/2020年形式の分離、`vasp_util` の外部import、`pyproject.toml`、`fdmnes_util install script` の構成は変更していません。全28スクリプトの機能再現は未完了です。
