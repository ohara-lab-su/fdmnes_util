# インストールと使い方

Python 3.10以上が必要です。ファイルの読み込みと数値処理にはNumPyを使います。描画にはMatplotlib、ASEを使う構造変換にはASE、POSCARの読み込みには外部パッケージの `vasp-util` が必要です。

```console
python -m pip install 'fdmnes-util[plot]'
```

リポジトリの作業ツリーから導入する場合はトップディレクトリで次を実行します。構造変換も使う場合は `.[plot,structure]` を指定します。

```console
python -m pip install '.[plot]'
```

`fdmnes_util install` と `fdmnes_util install script` は、全サンプルをカレントディレクトリにコピーします。`fdmnes_util install FDplot_XAS` は `FDplot_XAS.py` だけをコピーします。`fdmnes_util install list` は、拡張子を除いたスクリプト名と説明を1行ずつ表示します。既存ファイルは `--force` を指定した場合に上書きします。`--directory` で別の作成済みディレクトリも指定できます。

```console
mkdir -p analysis
fdmnes_util install script --directory analysis
cd analysis
python FDplot_XAS.py --help
```

FDMNES本体で計算したファイルを解析ディレクトリに置きます。計算本体は別途用意してください。多くのサンプルは入力ファイルにある `Filout` を使って出力名を解決します。`FDplot_XAS.py` などでは `-i` を省略すると、作業ディレクトリの `fdmfile.txt` の先頭ジョブ、または `read_pdb.inp` を使います。

## Python から計算を実行する

手作業で作成した `Cu_inp.txt` をカレントディレクトリに置いたら、同じ場所で次を実行します。FDMNES 本体は別途用意し、`fdmnes` として起動できるようにします。

```console
fdmnes_util install FDrun
python FDrun.py Cu_inp.txt
```

Python からも同じ入力を実行できます。

```python
from fdmnes_util.fdm_run import FdmRun

FdmRun().run("Cu_inp.txt")
```

`FdmRun()` は `fdmnes` を使います。別の実行ファイルを使う場合は、そのパスを渡します。入力を指定すると、作業ディレクトリの `fdmfile.txt` をその入力1件で作成または書き換えます。一覧は実行後も残ります。引数なしの `FDrun.py` と `run()` は、既存の `fdmfile.txt` をそのまま使います。指定した入力や必要な一覧がなければ起動前にエラーになります。

作業場所の既定はカレントディレクトリです。本体は入力の `Filout` に従って計算結果を書き出します。標準出力は実行中に画面に表示され、同じ内容を作業ディレクトリの `fdmnes-*.log` にも保存します。

材料、構造、化学量論比が異なる入力を用意すれば、Python で選択や実行順を決められます。例えば `FdmRun().run_inputs(["Cu_inp.txt", "Cu2O_inp.txt", "CuO_inp.txt"], directory=".")` は各入力について本体を1回ずつ起動します。結果を分けるには、各入力で異なる `Filout` を指定します。

## 計算入力を作成・更新する

新規入力を作るには `model = FdmInp(None, format_year=2026)` で空の入力から始めます。`save()` は終端の `End` がなければ自動で補います。FDMNES の入力本文をすでに文字列で持っている場合は `FdmInp.from_text(text)` を使います。

格子定数と原子行を Python で組み立てる場合は `set_structure()` に渡します。POSCAR から始める場合は `FdmInp.from_poscar("POSCAR")` を使います。構造の読み込みを `vasp_util`、FDMNES 形式への変換を `FdmStructure` が担当します。以下は保存済み入力を開いて計算条件を更新する例です。

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

model = FdmInp("cu.inp", format_year=2026)
model.set_filout("Cu_radius_scan")
model.set_range(-2, 0.2, 5, 0.5, 10, 1, 40)
model.set_radius(4.0, (15, 3.5), (30, 3.0))
model.set_green()
model.set_convolution()
job = model.save("cu_radius.inp")
FdmRun().run(job, timeout=120)
```

`set_range()` で刻み幅を途中で変える場合は、下限の次に刻み幅と区間の上限を順に指定します。`set_radius()` の最初の値は半径（Å）です。後続の組は切替エネルギー（eV）と切替後の半径です。計算条件の解釈は FDMNES 本体が行います。`save()` は既存ファイルがあればエラーにし、`overwrite=True` で明示的に上書きできます。

`run_inputs()` は各起動の終了結果を `subprocess.CompletedProcess` のリストで返します。各起動で一覧に書く入力は1件です。入力と参照データの相対パスは計算フォルダ基準です。タイムアウトは一覧全体に適用されます。

### マニュアルの計算例

```console
python FDmanual_examples.py all --directory manual_calculations
python FDmanual_examples.py poscar --poscar POSCAR --directory poscar_calculation
```

`all` はマニュアルの FCC 銅、最初の計算例の磁鉄鉱、分子構造例の FeO₆ を順に実行します。FeO₆ には短い Fe K 吸収端計算を設定しています。`--write-only` で入力生成だけを行えます。

## ドキュメントをローカルで表示する

リポジトリのトップディレクトリで次を実行します。生成先は `docs/_build/html/` です。

```console
python -m pip install . -r docs/requirements.txt
bash docs/build.sh
python -m http.server 8000 --directory docs/_build/html
```

ブラウザで `http://localhost:8000/` を開きます。`/en/` は英語版、`/ja/` は日本語版です。
