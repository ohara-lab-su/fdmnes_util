# SAE原本ヘッダ移植の照合結果

SAEの冒頭コメントは歴史的資料として原文のまま保存しました。古いクラス名や仕様の記述を現行仕様と混同しないよう区切っています。

- `fdm_bav.py` ← `sae/fdmnes/bav.py`：原本冒頭コメント 42 行を原文で収録。
- `fdm_bav_2016.py` ← `sae/fdmnes/bav_2016.py`：原本冒頭コメント 39 行を原文で収録。
- `fdm_bav_2020.py` ← `sae/fdmnes/bav_2020.py`：原本冒頭コメント 42 行を原文で収録。
- `fdm_conv.py` ← `sae/fdmnes/conv.py`：原本冒頭コメント 43 行を原文で収録。
- `fdm_inp.py` ← `sae/fdmnes/inp.py`：原本冒頭コメント 80 行を原文で収録。
- `fdm_sd.py` ← `sae/fdmnes/sd.py`：原本冒頭コメント 76 行を原文で収録。
- `fdm_sd_2016.py` ← `sae/fdmnes/sd_2016.py`：原本冒頭コメント 104 行を原文で収録。
- `fdm_sd_2020.py` ← `sae/fdmnes/sd_2020.py`：原本冒頭コメント 99 行を原文で収録。
- `fdm_structure.py` ← `sae/fdmnes/structure_writer.py`：原本冒頭コメント 83 行を原文で収録。
- `fdm_txt.py` ← `sae/fdmnes/txt.py`：原本冒頭コメント 55 行を原文で収録。
- `fdmfile.py` ← `sae/fdmnes/fdmfile.py`：原本冒頭コメント 25 行を原文で収録。

この一覧以外のモジュールについては、原本との由来の対応を確定していません。由来を推測してコメントを移植していません。

## 追加の照合

- `fdm_inp.py` には入力の読み込み元 `sae/fdmnes/inp.py` に加え、書き出し元 `sae/fdmnes/inp_writer.py` の冒頭コメントを掲載。
- `fdmfile.py` には `sae/fdmnes/fdmfile.py` と `sae/fdmnes/fdmfile_writer.py` の冒頭コメントを掲載。
- `athena_nor.py` に `sae/athena/nor.py` の冒頭コメントを掲載。
- `FDclean.py`、`FDmove.py`、`FDfdm2vasp.py`、`FDmakeCconvAllsite.py`、`FDbav2xyz.py`、`FDplot_XAS.py`、`FDplot_XASs.py` に各原本から署名と履歴コメントを掲載。
