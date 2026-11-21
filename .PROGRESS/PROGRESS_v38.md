# rebuild v38

- SAE `fdPDOS_XAS_av.py` の `--label` と `--atom` の軌道曲線ラベル規則を復元。
- `--label` がない場合は `<atom>-<orbital>`、指定時は `<label>-<orbital>`。
- 編集可能なサンプル `scripts/fdPDOS_XAS_av.py` に実装し、専用の回帰テストを追加。
- 数値処理・ファイル形式別クラス・サンプル配布コマンドは変更していない。
- 28本の完全再現、原本ヘッダ監査、docstringの内容確認、Black整形は未完了。
