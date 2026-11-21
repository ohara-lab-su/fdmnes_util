# fdmnes_util — FDMNES計算入力・出力の解析ライブラリ

## 位置づけ

`fdmnes_util` はFDMNESの入力ファイル、計算ログ、吸収スペクトル、SD（状態密度）出力を**ファイル形式別のクラス**として扱う独立ライブラリです。2016形式と2020形式のSD、BAVは独立クラスです。2022年版の形式は実データ照合後に追加し、2020形式と同一であると仮定しません。

## 開発の経緯

本ライブラリの前身は、2014年前後から開発されたStructural Analysis Environment（SAE）のFDMNES関連処理です。開発者は、pyFDMNESとほぼ同時期から解析支援ツールの開発を進めていました。SAEはFDMNESに限らない大規模環境へ成長したため、開発が途中で中断されました。本プロジェクトはFDMNES関連機能を抽出するのではなく、SAEの `FD*` / `fd*` スクリプトが持つ操作・解析・描画機能を単独パッケージに**再設計**するものです。前身: https://github.com/ohara-lab-su/sae 。SPring-8 BL14B2利用者情報での言及の正確な書誌情報は照合中です。

## クラス責務

- `ReadFdmInp` → `read_fdm_inp.py`: 計算入力 `.inp` のタグ・結晶パラメータ
- `ReadFdmfile` → `read_fdmfile.py`: `fdmfile.txt` ジョブ一覧
- `ReadFdmBav2016`、`ReadFdmBav2020` → 対応する `read_fdm_bav_20xx.py`: 計算ログ
- `ReadFdmSd2016`、`ReadFdmSd2020` → 対応する `read_fdm_sd_20xx.py`: SDの軌道・スピン・積分列
- `ReadFdmTxt`、`ReadFdmConv`: XANES、畳み込み後XANES
- `AnalyzeFdmXas`、`AnalyzeFdmLog`: ファイル読み出し以外の数値処理
- `PlotFdmXas`、`PlotFdmDos`: 描画
- `WriteFdmXyz`、`WriteFdmPhotoenergy`: 派生ファイルの生成

VASPのPOSCAR読込は `vasp_util.vasp_poscar.VaspPoscar` をモジュールimportします。VASPの内部実装は複製しません。

## 実行例

```python
from fdmnes_util.read_fdm_sd_2020 import ReadFdmSd2020
sd = ReadFdmSd2020('Fe_sd0.txt')
energy, d_dos = sd.get_eng(), sd.get_ldos('d')
```

## 実装状況

この版は再構築途中の成果物です。原本の全28コマンドを実行可能と主張しません。コマンドごとの差分は `COMMAND_AUDIT.md` に記載します。

## スクリプト対応状況

SAEの28本を個別に列挙した `COMMAND_AUDIT.md` を参照してください。11本は一部の操作に対応し、全オプションの同等性はまだ確認していません。

VASPファイルの変換機能を使用する場合は、独立パッケージ `vasp_util` を別途インストールしてください。配布名は実際の `vasp_util/pyproject.toml` を確認してください。
