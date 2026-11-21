# fdmnes_util

[日本語ドキュメント](https://ohara-lab-su.github.io/fdmnes_util/ja/) · [English documentation](https://ohara-lab-su.github.io/fdmnes_util/en/)

[SAE原本とのスクリプト比較](docs/ja/scripts.md)

FDMNESの計算入力・出力ファイルを扱うためのPythonクラスライブラリです。

FDMNESでは、計算条件を記述する入力ファイルのほか、計算ログ、XANESスペクトル、状態密度（SD）、畳み込み後のスペクトルなど、目的の異なるファイルが出力されます。本ライブラリでは、これらを**ファイルの種類ごとに独立したクラス**として扱います。ファイルの読み込みと、スペクトルの数値処理、グラフ作成は別のクラスに分けています。

## 開発の経緯

本ライブラリの元になったプログラムは、[Structural Analysis Environment（SAE）](https://github.com/ohara-lab-su/sae) のFDMNES関連ツールです。FDMNESを利用したXANESの計算・解析を支援するため、pyFDMNESとほぼ同じ時期から開発してきました。当時は研究で必要となった解析プログラムをその都度作り、SAEの一部としてまとめていました。

その後、SAEはFDMNES以外の構造解析も含む大きなプログラム群になりました。一方、FDMNES関連ツールの開発は途中で止まっていました。今回、これまでのコードをそのまま移すのではなく、計算入力・出力ファイルの形式を中心にクラスを組み直し、単独のパッケージとして整備することにしました。SAEの `FD*` / `fd*` スクリプトが持っていた解析・描画機能も、個別のクラスへ移していく方針です。

SAEの開発については、SPring-8 BL14B2の利用者情報にも記録があります。該当する年度・記事を確認し、書誌情報が特定できたものから追加します。開発者が関わったXAFS研究では、SAEを解析環境として使用してきました。研究論文ではFDMNESによる計算に言及していても、SAEそのものを明示していない場合があります。SAEの開発中断と、研究での利用実績は別の話です。

## クラスの構成

ファイル形式ごとにクラスを設け、必要な読み込みと書き出しを同じクラスで扱います。FDMNESの版によって形式が異なる場合は別のクラスにしています。

| ファイル | クラス | 主な内容 |
| --- | --- | --- |
| `*.inp` | `FdmInp` | 計算条件、`Filout`、結晶情報 |
| `fdmfile.txt` | `Fdmfile` | 複数入力ファイルの一覧 |
| `*_bav.txt` | `FdmBav2016` / `FdmBav2020` | 計算ログ、原子情報、エネルギー |
| `*_sd*.txt` | `FdmSd2016` / `FdmSd2020` | LDOS、PDOS、TDOSなど |
| `*.txt` | `FdmTxt` | XANESスペクトル |
| `*_conv.txt` | `FdmConv` | 畳み込み後のスペクトル |

クラス名は `FdmSd2016`、ファイル名は `fdm_sd_2016.py` のように、Pythonの命名規則に従って対応させています。2016年形式と2020年形式は別クラスです。2022年版については、実際の出力を照合するまでは2020年形式と同じものとして扱いません。

ファイルから読み出した値を使う処理は `AnalyzeFdmXas`、`AnalyzeFdmLog` などの解析クラスが担当します。グラフ作成は `PlotFdmXas`、`PlotFdmDos` が担当します。**スクリプトには解析式や描画処理を重複して書かず、これらのクラスを呼び出す形**にします。

## クラスライブラリ API

`src/fdmnes_util` の公開クラスを Python から直接使うための資料です。

- [手書き API リファレンス](docs/ja/manual_reference.md) クラスごとの import 文、メソッドの引数と戻り値、Python の使用例。
- [Sphinx 自動生成 API](https://ohara-lab-su.github.io/fdmnes_util/ja/api/) ソースのシグネチャと docstring。

## 使用例

2020年形式のSDファイルから、エネルギー軸とd軌道の状態密度を取り出す例です。

```python
from fdmnes_util.fdm_sd_2020 import FdmSd2020

sd = FdmSd2020("Fe_sd0.txt")
energy = sd.get_eng()
d_dos = sd.get_ldos("d")
```

VASPのPOSCARは、別パッケージの `vasp_util` をPythonモジュールとしてimportして扱います。VASP用の読み書き処理をこのパッケージに複製する方針ではありません。

## サンプルスクリプトのインストール

このライブラリのスクリプトは、利用者が手元で編集して使うためのサンプルプログラムです。Pythonパッケージをインストールした後、解析を行いたいディレクトリで次のコマンドを実行してください。

```console
fdmnes_util install script
```

パッケージに収録されたサンプルスクリプトが、カレントディレクトリへコピーされます。例えば `FDplot_XAS.py` を開くと、XASファイルの読み込みからグラフの生成まで、クラスライブラリの使い方を実際のPythonコードとして確認できます。計算条件や描画方法は、コピーしたスクリプトを自由に書き換えてください。

既存の同名スクリプトは上書きしません。上書きする場合に限り `--force` を指定します。コピー先を変える場合は `--directory` を使用できます。

```console
fdmnes_util install script --directory ./analysis
fdmnes_util install script --force
```

配布するスクリプトの編集元は、リポジトリ直下の `scripts/` です。`pyproject.toml` の設定で、インストール用のスクリプトをwheelに収録します。`setup.py` は使用しません。ライブラリ本体には解析や描画のアルゴリズムを実装し、各スクリプトはその具体的な利用例として記述しています。

SAEの対象28本に対応する編集用サンプルを収録しています。オプションや出力の再現状況は監査表を参照してください。

## スクリプトの再構築

対象は、SAEにあった `FD*` / `fd*` の全28本です。コマンド名だけを残すのではなく、各スクリプトに書かれている機能をファイル読み込み・解析・描画クラスへ整理し、同じ操作を再現することが目標です。

現段階では、28本すべての機能を再現できていません。対応状況と、まだ確認できていないオプションは [`COMMAND_AUDIT.md`](.PROGRESS/COMMAND_AUDIT.md) に記載しています。

`FDplot_XASs` は、複数サイトの畳み込みスペクトルを読み込んで表示します。元の `-o` は実験データの表示指定として扱います。Athenaの `*_obs.txt.nor` は `AthenaNor` で読み込みます。Fermi準位基準への変換も解析クラスに分離しています。旧スクリプトの全オプションとの一致は引き続き確認が必要です。元のスクリプトと完全に同等という意味ではありません。

## 関連資料

- [SAE（Structural Analysis Environment）](https://github.com/ohara-lab-su/sae)
- [尾原研究室の公開ソフトウェア](https://ohara-lab-su.github.io/)


## コードの記述規則

Pythonファイルにはシバン行とdocstringを記載し、クラスや公開メソッドの説明にはGoogleスタイルを使用します。条件分岐や処理の途中経過を省略せず、人が読んで処理を追える書き方を優先します。

## プロットクラスの配置

グラフ描画を担当するクラスは `fdmnes_util.plot` にまとめ、コマンドと分離しています。XASとサイト別LDOSを組み合わせた図は `FDplot_XAS_LDOS` で出力できます。SD形式は `--year 2016` または `--year 2020` で明示します。

## `fdLDOS0_specified` の再構築

元のスクリプトで使用していた `--emin`、`--emax`、`--dmax` を引き継ぎ、p軌道のLDOSを描画するコマンドを追加しました。計算結果の保存先は固定せず、入力ファイルの `Filout` を参照します。読み込みは年度別の `FdmSd2016` または `FdmSd2020` が担当し、描画は `PlotFdmDos` にまとめています。

```console
python fdLDOS0_specified.py -i read_pdb.inp --year 2020 --emin -10 --emax 20 --dmax 3
```

EPS、PDF、PNGを出力します。元のスクリプトが持っていた対話的な画面表示は、このコマンドでは行いません。2022年形式は実データを確認できていないため、2020年形式として処理しません。


`fdXAS_specified.py` のサンプルも追加しました。元のSAEスクリプトにあるフェルミ準位基準のエネルギー変換は解析クラスが担当し、描画は `plot/` のクラスを使用します。

## VASPとの連携

POSCARの読み込みは、別パッケージの `vasp_util` に任せています。`fdmnes_util` にVASP用のパーサーは実装しません。`FDvasp2fdm.py` は `VaspPoscarFile` を通してPOSCARを読み込み、`FdmStructure` でFDMNESの構造部分を書き出すサンプルです。

```console
fdmnes_util install script
python FDvasp2fdm.py -i POSCAR
```

`FDfdm2vasp.py` は ASE を使い、FDMNES の `Crystal` または `Molecule` から POSCAR を書き出します。分子の場合は `--vacuum`（既定値は片側10 Å）で真空幅を指定できます。

`FDvasp2fdm.py` は、POSCARから構造ファイルと計算条件付きの `read_pdb.inp` を作成します。入力ファイルの生成は `FdmInp`、結晶構造の出力は `FdmStructure` が担当します。


## クラスの命名

FDMNESのファイル形式を単位としてモジュールとクラスを分けます。読み込みと書き出しでクラスを分割せず、`fdm_inp.py` の `FdmInp`、`fdmfile.py` の `Fdmfile` などが同じファイル形式の操作を担当します。年度によって形式が異なるBAVとSDは `FdmBav2016` / `FdmBav2020`、`FdmSd2016` / `FdmSd2020` に分けます。

## CIF変換サンプル

`FDcif2fdm.py` を追加しました。原本はCIFを読み込んだ後 `bug version` と表示して終了するため、変換処理は原本に存在しない拡張実装です。ASEでCIFを読み込み、`Cif` と `FdmStructure` を利用します。

### SD形式の選択

SDファイルの形式は `FdmSd` クラスで明示的に指定します。`FdmSd(..., format_year=2016).select_reader()` または `format_year=2020` を使用します。未確認の年度形式を自動的に2020年形式と同一視しません。

### 複数計算のPDOS平均化（v28）

`fdPDOS_XAS_av.py` は複数のSDファイルを読み込み、エネルギー格子の一致を確認して軌道別PDOSを平均化する編集可能なサンプルです。SAE原本のXAS同時表示やエネルギー基準切り替えなどは未移植です。

`fdMulti_3.py` のサンプルを追加しました。3つの独立した計算結果のLDOSを、それぞれのフェルミ準位を基準として比較します。

### v37: 平均XASの重ね合わせ

`fdPDOS_XAS_av.py` の `--xas-files` に畳み込み後XAS、`--raw-xas-files` に畳み込み前XASを指定すると、両者の平均スペクトルを重ねて描画できます。異なるエネルギー格子は混用せず、別々に平均化します。SAE原本のエネルギー基準変換は未再現です。

### v40: 平均PDOS/XASのエネルギー基準

`fdPDOS_XAS_av.py` は `--input` と `--raw-xas-files` を指定すると、入力の光子エネルギーモードとXASの吸収端・フェルミ準位を使ってエネルギー軸を変換します。`--fermi` でフェルミ準位基準を選択します。`--energy-offset` は追加の補正です。
