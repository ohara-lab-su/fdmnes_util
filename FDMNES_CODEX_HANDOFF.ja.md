# fdmnes_util 開発引き継ぎ書

確認日 2026年11月22日（日本時間）

## 次のCodexへの依頼

`/Users/nakada/zaiene_dev/fdmnes_util` をプロジェクトフォルダとして開き、既存の `fix/fdmnes-compat-2026` ブランチで修正を続ける。目的は、**SAE原本に基づく現行のクラスライブラリで、確認済みのFDMNES出力と入力を正しく扱うこと**。SAEの処理を実装の基準とし、先に2019年・2020年の実出力を基準として確定させる。そのうえで、2021年・2026年の実計算から分かった未対応箇所を、根拠のある最小の差分で直す。

リポジトリとブランチはコード・テスト・文書を編集する場所。**FDMNESの実行、生成ファイル、pytest、Sphinxのビルドは、それぞれ専用の一時ディレクトリにコピーして行う。** 元の入力・計算結果・FDMNES実行ファイル・データファイルには書き込まない。本書を作成した時点では、直近に依頼された追加修正の調査までで中断しており、以下の未対応事項は実装していない。

## 1. ブランチと作業ツリー

| 項目 | 確認した状態 |
| --- | --- |
| PyCharm / Codexで開くプロジェクト | `/Users/nakada/zaiene_dev/fdmnes_util` |
| チェックアウト済みブランチ | `fix/fdmnes-compat-2026` |
| HEAD | `87101cb2eb1bdf089835737e35f95447692e8de9` (`Stop tracking .PROGRESS directory`) |
| ステージ済み | `src/fdmnes_util/fdm_bav_2026.py` の追加 |
| 未ステージの既存修正 | 日英のAPI索引・手書きAPI・スクリプト説明、SDを使う描画スクリプト、BAV・SD・入力・XAS・XYZ関連の実装とテスト |
| 本書作成前からの未追跡テスト | `tests/test_bav_2026.py`、`tests/test_sae_composite_plots.py` |
| 過去の一時クローン | 作業中に言及された `cbdc9d0` は現リポジトリのオブジェクトとして確認できなかった。現行の作業ツリーが引き継ぎの起点 |

作業開始時は以下を読み取り専用で確認する。

```bash
cd /Users/nakada/zaiene_dev/fdmnes_util
git --no-optional-locks status --short --branch
git rev-parse HEAD
git diff --cached --stat
git diff --stat
```

- `main` はGitHub側のPR用、`develop` は利用者のローカル開発の基準。どちらにもチェックアウト、編集、マージ、pushを行わない。ユーザーがチェックアウト済みのfixブランチをそのまま使う。
- 既存のステージ状態と、利用者・前作業から残っている差分を保存する。過去のパッチや一時クローンをまとめて取り込むとSAEから離れた作業が戻るおそれがある。必要な比較は個別の原本と現行ソースで行う。コミット・push・PR作成は個別の指示があったときに行う。
- 旧版・現行版のクラス名、公開メソッドのシグネチャと既定値、戻り値の型、正常系の契約、既存コメントや原著者表示を維持する。複数件を返す必要があるときは、既存の単値APIの互換性を保ったうえで、必要最小限の追加APIを検討する。
- 年号を付ける場合は実出力で確認できた形式差と対応させる。同じ行・列の形式が複数年で出ている場合は、既存のSAE由来処理と共通化できる範囲を確認する。確認していない年の互換性を推定で宣言しない。`FdmBav2026` のファイルは先行作業で保留されていたため、まず既存実装を読み取り、共通処理と選択経路から検討する。2026固有と確認できた処理が必要な場合にだけ対象箇所を見直す。
- この会話の要点には誤った初期判断があった。**2026年で初めて大きく書式が変わったとは確認されていない。** 2021年・2026年の両方で確認された記録を「2026年専用」と分類しない。

## 2. 原本と過去の照合資料

使用した原本は、ユーザー指定のアーカイブを格納した [配布一式](/Users/nakada/Downloads/FDMNES_CODEX_HANDOFF_COMPLETE.zip)。内部パスは `FDMNES_CODEX_HANDOFF/sources/sae_original.zip` と `FDMNES_CODEX_HANDOFF/sources/vasp_util_original.zip`。当初指定された `/Users/nakada/Desktop/FDMNES_CODEX_HANDOFF/sources/` は引き継ぎ時点では見つからなかった。

| 資料 | 所在または確認値 |
| --- | --- |
| SAE原本ZIPのSHA-256 | `fa8b95e8dc58863642cdb02b6060efd4e0ecdff31323fb20e56ff5b004aee3bb` |
| vasp_util原本ZIPのSHA-256 | `0d3b05c7fb4e91e6525bbff3315aa057e17c9570920fea3d4b14063826c5600a` |
| 同梱のハッシュ表 | `FDMNES_CODEX_HANDOFF/docs/SOURCE_SHA256.txt` |
| 既存28クラス・公開と非公開を含む148メソッドの照合 | [クラス別照合と行差分](/private/tmp/fdmnes-2020-line-audit.wCTilS/クラス別照合.md) · [照合報告](/private/tmp/fdmnes-2020-line-audit.wCTilS/照合報告.md) |
| 既存の原本展開場所 | `/private/tmp/fdmnes-2020-line-audit.wCTilS/sources/sae/sae` |
| FDMNES 2020年8月の取扱説明書 | [Manual_Eng_2020_08.pdf](/Users/nakada/physics/WORKS_sp8/JASRI_XAFS/FDMNES_2020.08/Manual_Eng_2020_08.pdf) |
| スクリプト説明の文体と構成の参照 | [SAEの日本語README](https://github.com/ohara-lab-su/sae/blob/main/README.ja.md) |

一時資料が消えた場合はZIPを新しい一時ディレクトリに展開し直す。コードの根拠は、公開リポジトリの最新状態から推定せず、ユーザー指定のZIP内のファイルと行番号を示す。別の場所から実行ファイルや資料を得た場合は、取得元、ファイル名、版、確認できるハッシュを報告する。取扱説明書や添付資料は仕様の参照として扱う。

```bash
fdm_sae_dir=$(mktemp -d /private/tmp/fdmnes-sae-source.XXXXXX)
fdm_handoff_archive=/Users/nakada/Downloads/FDMNES_CODEX_HANDOFF_COMPLETE.zip
unzip -p "$fdm_handoff_archive" 'FDMNES_CODEX_HANDOFF/sources/sae_original.zip' > "$fdm_sae_dir/sae_original.zip"
shasum -a 256 "$fdm_sae_dir/sae_original.zip"
unzip -q "$fdm_sae_dir/sae_original.zip" -d "$fdm_sae_dir"
```

## 3. SAEベースへの修正済み部分

| 箇所 | 現行の処理と根拠 |
| --- | --- |
| BAV見出し | SAE原本の `FDMNES.*program,` に沿って `FDMNES II program` を読む。2019年Cuの実BAV 1行目で確認済み |
| BAVの複数表 | 原本の上書き処理に従い、クラスタ位置と変換行列は最後の対応表を採る。2021年・2026年のFe複数サイト実出力にもクラスタ表が2つあり、最後の表と照合済み。公開 `get_edge()` は従来どおり完全ラベルを返す |
| SD形式選択 | `FdmSd(path, format_year=None)` はSD自身の列名で選択する。2019年Cuは `Int_t` を持つ26列の2016形式、2020年Feは `total` を持つ17列の2020形式。明示指定の `format_year=2016/2020` と従来の `format_from_bav` は維持。新規の自動判定はSDの列を使う |
| SDの既存不具合対策 | 2020年FeのTDOSは原本が初期化したゼロ配列を返すが、実ファイル2行目の `total` は `4.06360E-07`。現行の実列を返す変更を維持。Cuの `get_pdos(l=1, m=0)` は実際の `n(1,0)` 列を返す。SAEのSD2016 getterは `n(1,-1)` 相当を選んだ後、読み取り専用 `ymax` への代入で失敗する |
| FdmInpの単値 | `File_out` の別表記を認識。キーワード自体が繰り返された場合は最後の定義を使うというSAEの走査に合わせた。入力内の一つのブロックに複数値がある場合は第5節に記す |
| XAS・XYZの出力 | XYZの固定幅、生・畳み込み平均XASの見出し・空行、光子エネルギー書出しの空行と精度を原本に沿わせた。2019年Cu・2020年Feのコピーでバイト単位の書式を照合した |

この時点のテストは **131件通過**。日英のSphinxビルドはルート英語・`en/`・`ja/` の3件成功。ただし後から行った実計算で第5節の未対応が判明している。[pytestログ](/private/tmp/fdmnes-sae-restore.c4inFn/pytest.log) · [Sphinxログ](/private/tmp/fdmnes-sae-restore.c4inFn/sphinx.log)

## 4. 比較に使う実ファイルと実行ファイル

### 2019年Cu／2020年Feの過去の実出力

| ケース | 元ディレクトリ（読み取り専用） | コピーして使うファイル |
| --- | --- | --- |
| 2019年Cu | `/Users/nakada/physics/WORKS_sp8/JASRI_XAFS/XAFS講習会_返信/XAFS2019_昭和電工/sim/Cu1K4AcO8_r6` | `inp.txt` と `Cu1K4AcO8.txt`、`Cu1K4AcO8_bav.txt`、`Cu1K4AcO8_conv.txt`、`Cu1K4AcO8_sd0.txt` |
| 2020年Fe | `/Users/nakada/fdmnes9/Fe3O4/new/new/16d/R6` | `read_pdb.inp` と `Fe.txt`、`Fe_bav.txt`、`Fe_conv.txt`、`Fe_sd0.txt`。4出力は現リポジトリの `tests/fixtures` とバイト単位で一致 |

2019年Cuは生XAS・畳み込みXAS各111点、2020年Feは各131点。軸と第1強度列、BAVの座標・変換行列などが原本と一致した。この検証は保存済み実出力の読み取り。2020年FeのBAVには非空のSCF履歴がないため、2020年のSCF記録書式を同ファイルから確定することはできない。[Cu検証ログ](/private/tmp/fdmnes-sae-restore.c4inFn/cu-2019.log) · [Fe検証ログ](/private/tmp/fdmnes-sae-restore.c4inFn/fe-2020.log)

### 2021年／2026年の新規実計算

今回確認した一時フォルダは `/private/tmp/fdmnes-live-test.gkkp10`。BAV先頭に記録された改訂日は2021年6月29日と2026年11月5日。どちらもFe SCF、Ni磁性、Fe 2吸収サイトを完走し、終了コード0かつ期待したファイルを新規生成した。

| 実行ファイル | 実際の所在と確認事項 |
| --- | --- |
| 2021 x86_64 | インストール先は `/Users/nakada/fdmnes/bin/fdmnes`、実行に成功したコピーは `/private/tmp/fdmnes-live-test.gkkp10/bin/fdmnes-2021-prior-copy`。SHA-256は `3ebec3c920730e4a9476afd7d880a64a21571d78469abc125ab97df0aad40f87`。インストール先からの最初のコピーは終了コード−9／タイムアウトとなった。以前の実行用コピーとインストール先のバイト一致を確認し、以前のコピーから再コピーして3件成功。原因は断定していない |
| 2026 arm64 | 実行に使ったコピーは `/private/tmp/fdmnes-live-test.gkkp10/bin/fdmnes-2026`。コピー元は先行テストの `/private/tmp/fdmnes-scf-magnetic.MnE2pN/2026/fdmnes_mac`。SHA-256は `34dca092424301970a73830928cc0e05f5e438bace8ccbb8bac1a7b36e8190da`。実行版は各BAV先頭で確認。上流配布アーカイブの来歴はここでは未確認 |

- 比較対象は `2021/{fe-scf,ni-magnetic,fe-sites}` と `2026/{fe-scf,ni-magnetic,fe-sites}`。各フォルダに入力、`fdmfile.txt`、`console.log`、BAV・生XAS・畳み込みXAS・SDが揃っている。復元・再計算は入力だけを新しいディレクトリへコピーして行う。
- ログと手順は [実行ファイルのハッシュ](/private/tmp/fdmnes-live-test.gkkp10/executables.txt)、[2026実行ログ](/private/tmp/fdmnes-live-test.gkkp10/run-summary.txt)、[2021再実行ログ](/private/tmp/fdmnes-live-test.gkkp10/retry-2021.txt)、[数値・制限の検証ログ](/private/tmp/fdmnes-live-test.gkkp10/verify-summary.txt)、[検証コード](/private/tmp/fdmnes-live-test.gkkp10/verify.py)。既存の `run.py` は期待ファイルが既に存在する場合に停止する仕様。既存検証フォルダ内で再実行せず、次回用コピーですでに生成された出力を入力フォルダへ持ち込まない。
- 現行の `FdmConvolutionInputs` と `Fdmfile` で生成した入力2件も2026版で実行し、各7点の畳み込みXASを取得した。[生成入力の実行記録](/private/tmp/fdmnes-live-test.gkkp10/2026/writer-generated/writer-check.txt)
- 直近の隔離検証でリポジトリのHEAD・ステージ状態・追跡差分・クラスソースおよびコピー元入力に変化がないことを確認した。[隔離検証](/private/tmp/fdmnes-live-test.gkkp10/isolation-check.txt)

## 5. 次の作業と受け入れ条件

### 優先1　BAVのSCF読取りを実出力に合わせる

- SAE原本 `sae/fdmnes/bav_2020.py` のSCF行は `Begining of cycle` と `Unit cell energy`（96–97行、127–131行）。この経路と現行の戻り値 `int`、`list[float]` を保つ。
- 2021年Feの実出力にも `Cycle …, Fermi energy = …` と `Total energy = … eV, Delta energy = …` がある。最終サイクル6、全エネルギー5件、最後は `-46303.7 eV`。現行の自動選択は `FdmBav2020` を返すが、値は `0` と `[]` になっている。[2021年実出力330–331行](/private/tmp/fdmnes-live-test.gkkp10/2021/fe-scf/Fe_SCF_bav.txt:330)
- 2026年Feは同系統の記録から最終サイクル8、全エネルギー7件、最後は `-43792.8 eV`。既存 `FdmBav2026` への直接指定では取得できるが、`FdmBav.select_reader()` は2026年を拒否する。[2026年実出力373–374行](/private/tmp/fdmnes-live-test.gkkp10/2026/fe-scf/Fe_SCF_bav.txt:373)
- 共通の認識条件を一か所に置けるか、既存の `FdmBav2026` とSAE由来のクラスを照合する。2026年の自動選択は今回実計算で確認した版や対応形式に根拠を持たせる。比較していない2022～2025年や将来の版を無条件に同じクラスへ送らない。磁性計算などにあるフェルミエネルギーだけの `Cycle` 行はSCF履歴として数えない。吸収原子の `Excited atom total energy` もSCF全エネルギーとして拾わない。複数サイトの最後の表、旧綴り、SCFなしの `0` と空リストも再確認する。

### 優先2　磁性SDを実列名で判定して読む

- 2021年・2026年のNi両方が31列。 `Energy`、`s_up`、`Int(s)_up`、`s_dn`、`Int(s)_dn`、p/dの軌道・積分列、末尾の `total`、`Int(total)` を含む。2026年だけの差として扱わない。現行の無指定判定と明示的な2020 readerの両方で拒否される。[2021見出し](/private/tmp/fdmnes-live-test.gkkp10/2021/ni-magnetic/Ni_mag_sd1.txt:1) · [2026見出し](/private/tmp/fdmnes-live-test.gkkp10/2026/ni-magnetic/Ni_mag_sd1.txt:1)
- SAEの `sae/fdmnes/sd_2020.py` にある軌道名・スピン指定と、現行の名前ベース抽出を基準に、実出力に存在するスピン付き列を取る。 `get_eng`、`get_densities`、`get_ispin`、`get_ldos`、`get_intldos`、`get_pdos` を検証し、上下スピンの各列と一致させる。 `total` と `Int(total)` は出力上では全スピン共通の列なので、スピン別の表があると仮定しない。既存の `get_tdos(spin=...)` / `get_inttdos(spin=...)` での扱いは、実ファイル・原本の処理・呼び出し元を照合してから決め、仕様を文書とテストで明示する。
- 2016形式と非磁性2020形式の既存テストを維持する。列のない形式に対して無関係な列を返したり、静かに0で埋めたりしない。現行の描画スクリプトからも、必要な引数を渡した場合に同じ結果になることを確認する。

### 優先3　FdmInpの複数値を、単値APIを保って読めるようにする

- SAE原本 `sae/fdmnes/inp.py` 198–215行には単値の読み取りがあり、同じキーワードを後で読み直した場合は代入で上書きする。現行はこの単値の挙動を戻している。しかし、有効な入力の **一つの `Absorber` ブロックの `1 2`** に対して `get_absorber()` は例外になる。FDMNESは両サイトの生XAS・SDを実際に生成する。[実入力9–10行](/private/tmp/fdmnes-live-test.gkkp10/2026/fe-sites/sites.inp:9)
- 一つの `Calculation` ブロックの **2ファイルと対応する重み・シフトの行** はFDMNESで有効。現行 `get_calculation()` は先頭ファイル名だけを返し、後続行は `tags` にあるだけ。既存の戻り値 `str` を保ちつつ、複数レコードの順序と数値フィールドを扱う小さな入口を検討する。[実入力1–8行](/private/tmp/fdmnes-live-test.gkkp10/2026/fe-sites/conv.inp:1)
- `Density` など `KEYWORDS` に登録されていない次のキーワードまで現行 `tags` に流れ込む例がある。実入力とマニュアルでブロックの境界を確認する。全入力処理を作り直したり、無関係な構造処理・描画を変更したりしない。既存の単値、インラインと次行指定、キーワード自体の繰返し、コメント、欠損時の既定、`File_out` 別表記を回帰確認する。複数値に対する従来単値getterの扱いを変更する場合は、その理由と挙動を明記する。

## 6. 作業の隔離と完了時の確認

1. 修正前に本書の根拠行と現行コードを読む。変更する処理を短く説明し、fixブランチのプロジェクトフォルダで必要なコード・テスト・文書だけを編集する。
2. `mktemp -d` で専用フォルダを作り、ケースごとにサブフォルダを設ける。FDMNESに渡す `fdmfile.txt` と `Filout` / `Conv_out` を確認し、出力をサブフォルダ内への相対パスにする。入力・実行ファイル・外部データを物理コピーし、元の計算フォルダや他ユーザーのフォルダを参照するシンボリックリンクや絶対パスを残さない。コピーに必要なCIF／PDBその他の外部参照があればそれもコピーして、一時入力側だけを調整する。FDMNESは各ケースの `cwd` を指定して実行し、コンソール出力と終了コードを保存する。
3. コードの検証もリポジトリから `src`、`scripts`、`tests`、`docs`、`pyproject.toml` をコピーした場所で実行する。以前の実績はPython `/Users/nakada/.pyenv/versions/3.12.11/bin/python`。利用可能な環境であることを先に確認する。
4. 既存の `verify.py` は現在の制限を `LIMIT` と記録する基準データ用で、未対応を期待する箇所がある。修正後は一時ディレクトリにコピーを作り、対象の制限を正しい値とのアサーションに置き換える。終了コード0だけで済ませず、BAVの日付、列見出し、対象行、戻り値の件数・数値を照合する。
5. 2019年Cuと2020年Feの保存済み実出力、2021・2026年のFe SCF／Ni磁性／Fe 2吸収サイトによるテストを実施する。コードによる入力生成の経路も該当する場合は再試験する。全pytestと日英Sphinxをコピー上で実行する。検証できなかった版・入力・既存機能は確認済みとして報告しない。
6. 手書きAPIは `docs/ja/manual_reference.md` と `docs/en/manual_reference.md` を更新し、日本語の内容を先に整える。クラスごとのPython例と全公開メソッドの引数・既定値・戻り値を保ち、追加・変更した分を埋める。自動生成APIは `docs/build.sh` で確認する。CLIの使い方が変わる場合だけ、該当する日英のスクリプト説明（原本の用途、現行の入出力、実行例、変更点）を更新する。
7. 完了報告には変更したクラスと根拠行、実行ファイルの所在・版、計算フォルダ、結果、残る制限を書く。**元の入力や計算結果を変更した事実があれば、特に計算実行によるものを、絶対パス・内容・経緯とともに必ず報告する。** 変更がないことを伝える場合も、元とコピーの比較と、テスト直前・直後のリポジトリ状態を確認する。

検証用のコピーを作る例。

```bash
cd /Users/nakada/zaiene_dev/fdmnes_util
fdm_isolated=$(mktemp -d /private/tmp/fdmnes-followup.XXXXXX)
fdm_python=/Users/nakada/.pyenv/versions/3.12.11/bin/python
mkdir -p "$fdm_isolated/project" "$fdm_isolated/mpl" "$fdm_isolated/calculations"
git --no-optional-locks status --porcelain=v1 > "$fdm_isolated/git-before-tests.txt"
git --no-optional-locks diff --binary HEAD > "$fdm_isolated/diff-before-tests.patch"
rsync -a --exclude=__pycache__ --exclude=_build src scripts tests docs pyproject.toml "$fdm_isolated/project/"
(
  cd "$fdm_isolated/project"
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$fdm_isolated/project/src" \
    MPLCONFIGDIR="$fdm_isolated/mpl" MPLBACKEND=Agg \
    "$fdm_python" -m pytest -q --basetemp="$fdm_isolated/pytest"
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$fdm_isolated/project/src" \
    PYTHON="$fdm_python" bash docs/build.sh
)
```

上のコピー先を検証に使い、修正を続けた場合は必要なソースを再コピーする。古い一時フォルダに残る実出力と、今回新しく生成した実出力を区別する。

### FDMNESの再実行例

前回の一時フォルダが残っている場合の例。下のコマンドはFeのSCF、Niの磁性、Feの複数サイトの入力とバイナリだけを新しい場所にコピーする。コピーした `run.py` は自分のあるフォルダを作業ルートとし、各ケースの `cwd` を個別に指定する。実行は期待するファイルがまだない場所で行うこと。

```bash
fdm_previous=/private/tmp/fdmnes-live-test.gkkp10
fdm_replay=$(mktemp -d /private/tmp/fdmnes-replay.XXXXXX)
fdm_python=/Users/nakada/.pyenv/versions/3.12.11/bin/python
mkdir -p "$fdm_replay/bin"
cp "$fdm_previous/bin/fdmnes-2021-prior-copy" "$fdm_replay/bin/"
cp "$fdm_previous/bin/fdmnes-2026" "$fdm_replay/bin/"
cp "$fdm_previous/run.py" "$fdm_replay/"
for fdm_version in 2021 2026; do
  for fdm_case in fe-scf ni-magnetic fe-sites; do
    fdm_destination="$fdm_replay/$fdm_version/$fdm_case"
    mkdir -p "$fdm_destination"
    cp "$fdm_previous/$fdm_version/$fdm_case/"*.inp "$fdm_destination/"
    cp "$fdm_previous/$fdm_version/$fdm_case/fdmfile.txt" "$fdm_destination/"
  done
done
"$fdm_python" -B "$fdm_replay/run.py" 2021 2026 > "$fdm_replay/run-summary.txt" 2>&1
```

既存のログを使う場合もコピーで検証する。2021年版と2026年版でNiの畳み込みXAS行数が43と58で異なった。検証では版間の出力を一律に数値一致させず、**各版のリーダーの戻り値が、その版が書いた実ファイルの列と一致するか**を調べる。
