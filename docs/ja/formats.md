# ファイル形式とエネルギー基準

| ファイル | 内容 | Pythonクラス |
| --- | --- | --- |
| `*.inp` | `Filout`、`Absorber`、`Energpho`、構造セクションなど | `FdmInp` |
| `fdmfile.txt` | ジョブ数と入力ファイルの順序付き一覧 | `Fdmfile` |
| `<Filout>.txt` | 生XASと吸収端・フェルミ準位のメタデータ | `FdmTxt` |
| `<Filout>_conv.txt` | 畳み込み後のエネルギー軸と強度 | `FdmConv` |
| `<Filout>_bav.txt` | リビジョン、計算条件、クラスタ座標、SCFログ | `FdmBav` |
| `<Filout>_sdN.txt` | サイトNの軌道別状態密度と積分値 | `FdmSd` |
| `*.nor` | Athenaで規格化した実験XAS | `AthenaNor` |

生XAS、畳み込み後XAS、SDのエネルギー格子は別々です。各ファイルの強度に対応するエネルギー列を使います。複数計算を平均する場合は、同種のファイル間で格子が一致している必要があります。

`AnalyzeFdmXas.energy_reference()` が使う規則を以下に示します。`E` はファイル内のエネルギー、`E_edge` と `E_Fermi` は生XASのヘッダにある値です。

| 計算入力 | 光子エネルギー | Fermi基準 |
| --- | --- | --- |
| `Energpho` なし | `E + E_edge` | `E − E_Fermi` |
| `Energpho` あり | `E` | `E − E_edge − E_Fermi` |

SDの2016年形式は列順と指定したスピン数で解釈します。2020年形式はヘッダの列名を使い、非磁性と、2021年・2026年の Ni 出力で確認した31列の磁性形式を読みます。磁性形式も `total` と `Int(total)` は上下スピン共通です。多くのサンプルでは `--year` で形式を選べます。

FDMNESの入力キーワードそのものは配布元のマニュアルを参照してください。この文書では本ライブラリが扱うファイルと操作を説明します。
