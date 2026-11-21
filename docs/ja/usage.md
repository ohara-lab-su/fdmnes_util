# インストールと使い方

Python 3.10以上が必要です。ファイルの読み込みと数値処理にはNumPyを使います。描画にはMatplotlib、ASEを使う構造変換にはASE、POSCARの読み込みには外部パッケージの `vasp-util` が必要です。

```console
python -m pip install 'fdmnes-util[plot]'
```

リポジトリの作業ツリーから導入する場合はトップディレクトリで次を実行します。構造変換も使う場合は `.[plot,structure]` を指定します。

```console
python -m pip install '.[plot]'
```

解析ディレクトリで `fdmnes_util install script` を実行すると、編集可能なPythonサンプル28本がコピーされます。既存ファイルはスキップされ、`--force` を指定すると上書きされます。`--directory` には作成済みのディレクトリを指定します。

```console
mkdir -p analysis
fdmnes_util install script --directory analysis
cd analysis
python FDplot_XAS.py --help
```

FDMNES本体で計算したファイルを解析ディレクトリに置きます。計算本体は別途用意してください。多くのサンプルは入力ファイルにある `Filout` を使って出力名を解決します。`FDplot_XAS.py` などでは `-i` を省略すると、作業ディレクトリの `fdmfile.txt` の先頭ジョブ、または `read_pdb.inp` を使います。

## ドキュメントをローカルで表示する

リポジトリのトップディレクトリで次を実行します。生成先は `docs/_build/html/` です。

```console
python -m pip install . -r docs/requirements.txt
bash docs/build.sh
python -m http.server 8000 --directory docs/_build/html
```

ブラウザで `http://localhost:8000/` を開きます。`/en/` は英語版、`/ja/` は日本語版です。
