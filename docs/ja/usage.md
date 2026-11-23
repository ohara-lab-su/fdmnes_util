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

```python
from fdmnes_util.fdm_run import FdmRun

log = FdmRun().run("Cu.inp")
print(log)
```

`FdmRun()` は PATH 上の `fdmnes` を使います。実行ファイルのパスも指定できます。`run()` は既定の `inp.txt`、`run("Cu.inp")` は指定した `Cu.inp` を1件だけ実行します。入力が存在しない場合は起動前にエラーになります。実行時は入力1件の `fdmfile.txt` を一時作成し、終了後に元の状態へ戻します。既存の一覧を使う場合は `run_fdmfile()` を呼びます。コマンドでは `python FDrun.py Cu.inp` または `python FDrun.py --fdmfile` を使います。


## 計算入力を作成・更新する

`FdmInp` は、マニュアルのキーワードとデータ行をその順序で書き出します。POSCAR から始める場合は `FdmInp.from_poscar("POSCAR")` を使います。構造の読み込みを `vasp_util`、FDMNES 形式への変換を `FdmStructure` が担当します。入力の作成時に選ぶ計算オプションは Python 側に記述できます。

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

model = FdmInp("cu.inp", format_year=2026)
model.set_block("Filout", "Cu_radius_scan")
model.set_block("Range", (-2, 0.2, 5, 0.5, 10, 1, 40))
model.set_radius(4.0, (15, 3.5), (30, 3.0))
model.set_block("Green")
model.set_block("Convolution")
job = model.save("cu_radius.inp")
log = FdmRun().run(job, directory=".", timeout=120)
print(log)
```

`set_radius()` の最初の値は半径（Å）です。後続の組は切替エネルギー（eV）と切替後の半径です。任意のキーワードは `set_block()` にデータ行を順に渡せます。`Calculation` など可変長ブロックを更新する場合は、差し替える元のデータ行数を `old_rows` で指定します。例えば `model.set_block("Calculation", "Cu.txt", (1.0, 0.2), old_rows=2)` です。マニュアルのようにキーワードを単独の行に置く入力を使用します。キーワードの組み合わせや計算条件は FDMNES 本体が解釈します。`save()` は既存ファイルがあればエラーにし、`overwrite=True` で明示的に上書きできます。

`run_inputs()` は Python で指定した順に1件ずつ本体を起動し、実行ログのパスを順に返します。各起動で一時一覧に書く入力は1件です。入力の相対パスと参照データは計算フォルダ基準です。タイムアウトは一覧全体に適用されます。

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
