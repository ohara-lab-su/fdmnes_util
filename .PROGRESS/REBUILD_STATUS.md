# fdmnes_util ベータ版の実装状況

- 計算入力は `fdmnes_util.fdm_inp.FdmInp`、ジョブ一覧は `fdmnes_util.fdmfile.Fdmfile` が読み込みと書き出しを担当する。
- BAV と SD は、それぞれ2016年形式と2020年形式のクラスを持つ。2022年版の非磁性FeO6出力1例を採取し、SDの17列ヘッダが2020年のFe実例と一致することを確認した。2022年形式の一般対応には追加の検証が必要。
- 解析は `analyze_fdm_*`、描画は `fdmnes_util.plot` に配置する。
- 編集用サンプル28本は `fdmnes_util install script` で配布する。操作単位の再現状況は [COMMAND_AUDIT.md](COMMAND_AUDIT.md) を参照。
- POSCARの読み込みは外部の `vasp_util`、`Crystal` からのPOSCAR出力は ASE が担当する。

残る作業には、SAE原本の各オプション・数値処理・図の照合、2016年の実出力と2022年の追加パターンによる検証が含まれる。

## 原本照合で修正した機能

| クラス | 実装と検証 |
| --- | --- |
| `FdmInp` | `Absorber`・`Magnetism` を読み込む。マニュアルに従い、分子の座標を実空間へ変換する。POSCARの真空幅はサンプルの追加設定。 |
| `Fdmfile` | 原本同梱のコメント付きバッチリストを読み込む。宣言された件数までをジョブとして扱う。 |
| `FdmBav2016`・`FdmBav2020` | SCFの有無・反復上限・最後のサイクル番号を扱う。2022年以降のログは年度選択で拒否する。 |
| `FdmSd2016`・`FdmSd2020` | 2016形式では原本のスピン名を扱う。2020形式は検証済みの単一スピン列に限定し、全取得メソッドでスピンを確認する。 |
| `FdmConvolutionInputs` | 生成ディレクトリから参照可能なパスを記述し、番号付きのスペクトルだけを処理する。 |
| `FdmResultFiles`・`FdmXyz` | Filoutの変更と結果ファイルの移動を扱う。XYZはファイルと標準出力で同じ書式を用いる。 |

`FDplot_XAS`・`FDplot_LDOS`・`FDplot_PDOS` の複合描画、保存形式、対話表示は
[監査表](COMMAND_AUDIT.md#composite-xas--ldos--pdos-verification) に記録した。
磁性かつ複数吸収端を含むXASの実データ検証、
`fdLDOS_color` の複合図、`fdPDOS_XAS_av` の配置・保存オプション、
標準XYZ変換のOpenMX MD入力が残る。

## FDMNESでの実行確認

ローカルの2022年6月15日版FortranソースをmacOS arm64向けにビルドした。
`FDmakeCconvAllsite.py` が既存のFeスペクトルに対して生成したジョブを実行し、
結果ディレクトリに `Fe_1_conv.txt` が作成されることを確認した。
