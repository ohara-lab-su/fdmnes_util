# rebuild v18

SAE原本 `sae(1).zip` にあるファイル形式別11モジュールの冒頭コメントを、改変・要約せずに原文で保存した。原本の歴史的記述と現行APIを区別する注記を付けた。照合結果は `SAE_HEADER_AUDIT.md` を参照。

今回の変更は原本ヘッダの正確性に限定した。28本のサンプルスクリプト再構築、他モジュールの由来照合、docstringの内容点検、Black整形は未完了。

確認: `PYTHONPATH=src python -m pytest -q` → 40 passed。
