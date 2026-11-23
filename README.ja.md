# fdmnes_util

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/fdmnes_util/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/fdmnes_util/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Ffdmnes_util-181717?logo=github)](https://github.com/ohara-lab-su/fdmnes_util/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/fdmnes_util/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)


FDMNESの計算入力・出力ファイルを扱うためのPythonクラスライブラリです。

FDMNESでは、計算条件を記述する入力ファイルのほか、計算ログ、XANESスペクトル、状態密度（SD）、畳み込み後のスペクトルなど、目的の異なるファイルが出力されます。本ライブラリでは、これらを**ファイルの種類ごとに独立したクラス**として扱います。ファイルの読み込みと、スペクトルの数値処理、グラフ作成は別のクラスに分けています。

## 開発の経緯

`fdmnes_util` は、2014年頃に開発した [Structural Analysis Environment（SAE）](https://github.com/ohara-lab-su/sae) のFDMNES関連プログラムを元にしています。当時はXANESの計算や解析で必要になった機能をSAEに追加していました。SAEの開発内容はSPring-8の刊行物などでも紹介しており、プログラム本体は関係者に直接渡していました。まだGitを使っていなかった頃のプログラムです。

当時、SPring-8 BL14B2ではXAFS利用者向けの講習会などを通じてFDMNESの紹介・普及にも取り組んでいました。その後、BL14B2からJASRIの制御・情報部門へ異動したこともあり、SAEのFDMNES関連プログラムの開発は止まりましたが、FDMNESの講習には引き続き関わっていました。当時の資料として、[2016年のFDMNES実習（PDF）](https://support.spring8.or.jp/new/assets/materials/190228_4.nakada_160128.pdf)、[2019年の講習会資料一覧](https://support.spring8.or.jp/new/event-materials.html)、[2019年のFDMNES実習（PDF）](https://support.spring8.or.jp/assets/materials/190228_5.nakada.pdf) が残っています。

最近、再びFDMNESを使う必要ができたので、10年以上前のプログラムを掘り出してきました。せっかくなので少し使ってみようと思い、現在のPython環境で動くように整備しています。あわせて、入出力ファイルを扱うクラスを整理し、SAEの `FD*` / `fd*` スクリプトに含まれていた解析・描画機能をライブラリへ移しています。

現在は [pyFDMNES](https://github.com/tinaw/pyFDMNES) などのライブラリもあります。ただ、FDMNESの計算実行全体を管理するラッパーを作ることには、今のところあまり関心がありません。まずは以前の解析機能を使えるようにし、現行のFDMNESのマニュアルも読み直しながら、研究で必要になった機能を追加していくつもりです。

## クラスの構成

ファイル形式ごとにクラスを設け、必要な読み込みと書き出しを同じクラスで扱っています。FDMNESの版によって形式が異なる場合は別のクラスにしています。

| ファイル | クラス | 主な内容 |
| --- | --- | --- |
| `*.inp` | `FdmInp` | 計算条件、`Filout`、結晶情報 |
| `fdmfile.txt` | `Fdmfile` | 複数入力ファイルの一覧 |
| `*_bav.txt` | `FdmBav2016` / `FdmBav2020` | 計算ログ、原子情報、エネルギー |
| `*_sd*.txt` | `FdmSd2016` / `FdmSd2020` | LDOS、PDOS、TDOSなど |
| `*.txt` | `FdmTxt` | XANESスペクトル |
| `*_conv.txt` | `FdmConv` | 畳み込み後のスペクトル |

クラス名は `FdmSd2016`、ファイル名は `fdm_sd_2016.py` のように、Pythonの命名規則に従って対応させています。2016年形式と2020年形式は別クラスにしています。2022年版については、実際の出力を照合するまでは2020年形式と同じものとして扱いません。

BAV の計算クラスタは年別の BAV リーダーで読み取ります。数値解析は `AnalyzeFdmXas` や `AnalyzeFdmAverage` が担当します。グラフ作成は `PlotFdmXas`、`PlotFdmDos` が担当します。**スクリプトには解析式や描画処理を重複して書かず、これらのクラスを呼び出す形**にしています。

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
fdmnes_util install
fdmnes_util install script
fdmnes_util install FDplot_XAS
fdmnes_util install list
```

`install` と `install script` は全スクリプトをカレントディレクトリにコピーします。`install FDplot_XAS` は `FDplot_XAS.py` だけをコピーします。`install list` は、個別指定に使う名前と日本語の説明を1行ずつ表示します。

`FDplot_XAS.py` を開くと、XASファイルの読み込みからグラフの生成まで、クラスライブラリの使い方を確認できます。計算条件や描画方法は、コピーしたスクリプトを自由に書き換えてください。

既存の同名スクリプトは上書きしません。上書きする場合に限り `--force` を指定します。コピー先を変える場合は `--directory` を使用できます。

```console
fdmnes_util install script --directory ./analysis
fdmnes_util install script --force
```

配布するスクリプトの編集元は、リポジトリ直下の `scripts/` です。`pyproject.toml` の設定で、インストール用のスクリプトをwheelに収録します。`setup.py` は使用しません。ライブラリ本体には解析や描画のアルゴリズムを実装し、各スクリプトはその具体的な利用例として記述しています。

SAEの対象28本に対応する編集用サンプルを収録しています。オプションや出力の再現状況は監査表を参照してください。

## FDMNES の計算を実行する

まず、計算に使う入力ファイルを手作業で用意します。ここでは、カレントディレクトリに `Cu_inp.txt` を置き、FDMNES 本体を PATH 上の `fdmnes` として起動できるものとします。同じディレクトリで [FDrun.py](scripts/FDrun.py) をコピーし、入力ファイル名を渡します。

```console
fdmnes_util install FDrun
python FDrun.py Cu_inp.txt
```

`FDrun.py` が FDMNES に必要な `fdmfile.txt` を入力1件分で用意します。同名の一覧がある場合は書き換えます。計算はカレントディレクトリで実行し、結果ファイルの保存先と接頭辞は入力の `Filout` に従います。本体の標準出力は画面に表示され、`fdmnes-*.log` にも保存されます。

## Python で計算入力を作成して実行する

次の例では、`FdmInp` で面心立方の銅の構造と計算条件を組み立て、`Cu_generated.inp` に保存します。保存したファイルを `FdmRun` に渡すと、手作業で作成した入力と同じ手順で FDMNES を起動します。

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

model = FdmInp.from_text("End\n")
model.set_block("Filout", "Cu_generated")
model.set_block("Absorber", 1)
model.set_block("Edge", "K")
model.set_block("Range", (-1.0, 0.2, 2.0))
model.set_radius(3.0)
model.set_block(
    "Crystal",
    (3.61, 3.61, 3.61, 90, 90, 90),
    (29, 0.0, 0.0, 0.0),
    (29, 0.5, 0.5, 0.0),
    (29, 0.5, 0.0, 0.5),
    (29, 0.0, 0.5, 0.5),
)
input_file = model.save("Cu_generated.inp")
FdmRun().run(input_file)
```

| メソッド | 用途 |
| --- | --- |
| `FdmInp.from_text(text)` | Python で用意した入力本文から始めます。例では終端の `End` だけを渡しています。 |
| `FdmInp.from_poscar("POSCAR")` | `vasp_util` で POSCAR を読み、FDMNES の構造節を作ります。 |
| `FdmInp(filename, format_year=2026)` | 保存済みの入力を編集用に開きます。 |
| `set_block(keyword, *rows)` | キーワードとデータ行を設定します。`Crystal` には格子定数と、原子番号・分率座標の各行を渡します。 |
| `set_radius(radius)` | 計算に使うクラスタ半径を Å 単位で設定します。 |
| `render_input()` / `save(filename)` | 現在の入力本文を確認するか、ファイルに保存します。`save()` は保存先のパスを返します。 |
| `FdmRun.run(input_file)` | 保存済みの入力ファイルを指定して FDMNES を起動します。 |

### 複数の入力を順に実行する

複数の計算では、Python で実行する入力と順序を自由に決められます。材料、結晶構造、化学量論比の異なる入力を用意し、たとえば Cu、Cu₂O、CuO を順に計算できます。それぞれの入力には異なる `Filout` を指定します。

```python
from fdmnes_util.fdm_run import FdmRun

runner = FdmRun()
for input_file in ("Cu_inp.txt", "Cu2O_inp.txt", "CuO_inp.txt"):
    runner.run(input_file)
```

同じ材料で計算条件だけを変える場合も、Python で入力を作れます。以下では `Cu_inp.txt` を元に計算半径を変え、入力ファイルと出力接頭辞を計算ごとに分けています。

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

runner = FdmRun()
for radius in (3.0, 4.0, 5.0):
    model = FdmInp("Cu_inp.txt", format_year=2026)
    prefix = f"Cu_R{radius:g}"
    model.set_block("Filout", prefix)
    model.set_radius(radius)
    input_file = model.save(f"{prefix}.inp")
    runner.run(input_file)
```

引数、単位、戻り値、既存入力を編集するときの注意点は、各メソッドの docstring から生成した API に記載しています。 [Sphinx 自動生成 API](docs/ja/api/index.md) · [API リファレンス](docs/ja/manual_reference.md)

## 同梱スクリプト一覧

同梱スクリプトは、このライブラリを使って構造変換、計算実行、結果の解析・描画を行う実例です。SAE の FDMNES 用スクリプトの操作を再現する例も含めています。

たとえば、サイト別 XAS の平均化は `AnalyzeFdmAverage.average()`、XAS・LDOS の複合図は `PlotFdmXas.plot_composite()` で、自分の Python コードから再利用できます。SAE 原版との対応や利用例には整備中の部分があり、今後も実際の計算や解析に使いながら見直していきます。

全33本を `fdmnes_util install script` でコピーできます。個別にコピーする場合は、表の名前を拡張子なしで指定します。例えば `fdmnes_util install FDrun` です。端末では `fdmnes_util install script list` で名前と説明を確認できます。 [スクリプトガイド](docs/ja/scripts.md)

| スクリプト名 | 用途 | 主に使うクラス |
| --- | --- | --- |
| [`FDbav2xyz`](scripts/FDbav2xyz.py) | BAV のクラスタ座標を XYZ に変換 | `FdmBav`, `Xyz` |
| [`FDcif2fdm`](scripts/FDcif2fdm.py) | CIF を FDMNES の構造節に変換 | `Cif`, `FdmStructure` |
| [`FDclean`](scripts/FDclean.py) | 指定した計算の出力を削除 | `FdmInp`, `ResultFileOperations` |
| [`FDconv_e2photoe`](scripts/FDconv_e2photoe.py) | 畳み込み XAS を光子エネルギー軸に変換 | `AnalyzeFdmXas`, `FdmConv`, `FdmPhotoenergy` |
| [`FDconv_sites`](scripts/FDconv_sites.py) | 重みとシフトを指定して複数サイトの畳み込み入力を作成 | `FdmInp` |
| [`FDfdm2vasp`](scripts/FDfdm2vasp.py) | FDMNES 入力の構造を POSCAR に変換 | `FdmStructure` |
| [`FDgetfermi`](scripts/FDgetfermi.py) | フェルミ準位と吸収端を表示 | `FdmTxt`, `FdmBav` |
| [`FDmakeCconvAllsite`](scripts/FDmakeCconvAllsite.py) | 全サイトの畳み込みジョブと一覧を作成 | `FdmInp`, `SiteConvolutionJobPreparer` |
| [`FDmanual_examples`](scripts/FDmanual_examples.py) | マニュアルの計算例や POSCAR から入力を作成・実行 | `FdmInp`, `FdmRun` |
| [`FDmove`](scripts/FDmove.py) | 指定した計算の出力を移動・改名 | `FdmInp`, `ResultFileOperations` |
| [`FDpbd2fdm`](scripts/FDpbd2fdm.py) | PDB を FDMNES の構造節に変換 | `Pdb`, `FdmStructure` |
| [`FDplot_LDOS`](scripts/FDplot_LDOS.py) | LDOS と必要に応じて XAS を描画 | `DosPlotWorkflow`, `PlotFdmDos` |
| [`FDplot_PDOS`](scripts/FDplot_PDOS.py) | 軌道別の PDOS と必要に応じて XAS を描画 | `DosPlotWorkflow`, `PlotFdmDos` |
| [`FDplot_SCF`](scripts/FDplot_SCF.py) | SCF の全エネルギーの推移を描画 | `FdmBav` |
| [`FDplot_SD`](scripts/FDplot_SD.py) | SD の軌道群や軌道射影を描画 | `FdmSd`, `PlotFdmDos` |
| [`FDplot_XAS`](scripts/FDplot_XAS.py) | 生 XAS・畳み込み XAS を描画し、実測 XAS や LDOS も比較 | `FdmTxt`, `FdmConv`, `AnalyzeFdmAverage`, `PlotFdmXas` |
| [`FDplot_XAS_LDOS`](scripts/FDplot_XAS_LDOS.py) | XAS と LDOS を同じ図に描画 | `FdmTxt`, `FdmConv`, `FdmSd`, `PlotFdmXasLdos` |
| [`FDplot_XASs`](scripts/FDplot_XASs.py) | 複数サイトの XAS を比較 | `FdmTxt`, `AnalyzeFdmXas`, `PlotFdmXas` |
| [`FDrun`](scripts/FDrun.py) | 入力1件または既存のジョブ一覧で FDMNES を起動 | `FdmRun` |
| [`FDvasp2fdm`](scripts/FDvasp2fdm.py) | POSCAR から FDMNES の構造節と計算入力を作成 | `VaspPoscar`, `FdmStructure`, `FdmInp` |
| [`FDvasp2fdm_BUG`](scripts/FDvasp2fdm_BUG.py) | SAE の旧版。変換は停止 | — |
| [`FDvasp2fdm_NEW_20151125_BUGversion`](scripts/FDvasp2fdm_NEW_20151125_BUGversion.py) | SAE の旧版。変換は停止 | — |
| [`FDxyz2fdm`](scripts/FDxyz2fdm.py) | XYZ を FDMNES の分子構造節に変換 | `Xyz`, `FdmStructure` |
| [`fdExp_comp_XAS`](scripts/fdExp_comp_XAS.py) | 計算 XAS と Athena の実測 XAS を比較 | `FdmTxt`, `FdmConv`, `AthenaNor`, `PlotFdmXas` |
| [`fdLDOS`](scripts/fdLDOS.py) | 指定したサイトと軌道の LDOS を描画 | `FdmSd`, `PlotFdmDos` |
| [`fdLDOS0_specified`](scripts/fdLDOS0_specified.py) | 試料ごとの設定を使って p-LDOS を描画 | `FdmSd`, `PlotFdmDos` |
| [`fdLDOS_color`](scripts/fdLDOS_color.py) | 占有領域を塗り分けて LDOS を描画 | `DosPlotWorkflow`, `FdmSd`, `PlotFdmDos` |
| [`fdLDOSmulti`](scripts/fdLDOSmulti.py) | 3サイトの LDOS を並べて描画 | `FdmTxt`, `FdmSd`, `PlotFdmDos` |
| [`fdMulti_2_XAS+LDOS+EXP`](scripts/fdMulti_2_XAS+LDOS+EXP.py) | 計算・実測 XAS と p-LDOS を二段で描画 | `FdmTxt`, `FdmConv`, `FdmSd`, `AthenaNor`, `PlotFdmXasLdos` |
| [`fdMulti_3`](scripts/fdMulti_3.py) | 3つの計算をフェルミ準位で揃えて比較 | `FdmTxt`, `FdmSd`, `PlotFdmDos` |
| [`fdPDOS_XAS_av`](scripts/fdPDOS_XAS_av.py) | 複数サイトの PDOS と XAS を平均して描画 | `AnalyzeFdmAverage`, `FdmSd`, `PlotFdmAverage` |
| [`fdXAS`](scripts/fdXAS.py) | 畳み込み XAS を描画 | `FdmConv`, `PlotFdmXas` |
| [`fdXAS_specified`](scripts/fdXAS_specified.py) | フェルミ準位を基準に XAS を描画 | `FdmTxt`, `FdmConv`, `AnalyzeFdmXas`, `PlotFdmXas` |

## スクリプトの再構築

対象は、SAEにあった `FD*` / `fd*` の全28本です。コマンド名だけを残すのではなく、各スクリプトに書かれている機能をファイル読み込み・解析・描画クラスへ整理し、同じ操作を再現することを目標にしています。

現段階では、28本すべての機能を再現できていません。対応状況と、まだ確認できていないオプションは [`COMMAND_AUDIT.md`](.PROGRESS/COMMAND_AUDIT.md) に記載しています。

`FDplot_XASs` では、複数サイトの畳み込みスペクトルを読み込んで表示します。元の `-o` は実験データの表示指定として扱います。Athenaの `*_obs.txt.nor` は `AthenaNor` で読み込みます。Fermi準位基準への変換も解析クラスに分離しています。旧スクリプトの全オプションとの一致は引き続き確認が必要です。元のスクリプトとの完全な同等性は、まだ確認できていません。

## 関連資料

- [SAE（Structural Analysis Environment）](https://github.com/ohara-lab-su/sae)

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

`FDvasp2fdm.py` は別パッケージの `vasp_util.vasp_poscar.VaspPoscar` で POSCAR を読み、`FdmStructure` で FDMNES の構造節を書き出します。FDMNES 入力から POSCAR へ変換する場合も、結晶・分子の構造の組み立ては `FdmStructure` が担当します。

```console
fdmnes_util install script
python FDvasp2fdm.py -i POSCAR
```

`FDfdm2vasp.py` は ASE を使い、FDMNES の `Crystal` または `Molecule` から POSCAR を書き出します。分子の場合は `--vacuum`（既定値は片側10 Å）で真空幅を指定できます。

`FDvasp2fdm.py` は、POSCARから構造ファイルと計算条件付きの `read_pdb.inp` を作成します。入力ファイルの生成は `FdmInp`、結晶構造の出力は `FdmStructure` が担当します。


## クラスの命名

FDMNESのファイル形式を単位としてモジュールとクラスを分けています。読み込みと書き出しでクラスを分割せず、`fdm_inp.py` の `FdmInp`、`fdmfile.py` の `Fdmfile` などが同じファイル形式の操作を担当します。年度によって形式が異なるBAVとSDは `FdmBav2016` / `FdmBav2020`、`FdmSd2016` / `FdmSd2020` に分けています。

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
