#!/usr/bin/env python3
"""fdmnes_util の日英ドキュメントのビルドを設定する。"""

import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / "src"))

project = "fdmnes_util"
author = "Ohara Lab"
root_doc = "index"
html_theme = "sphinx_rtd_theme"
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
myst_enable_extensions = ["colon_fence"]
autodoc_member_order = "bysource"
autodoc_default_options = {"inherited-members": True}


def _language_links(app, docname, source):
    """日英の HTML を相互に移動するためのバッジを生成する。

    Args:
        app: 対象言語版を構成する Sphinx アプリケーション。
        docname: Sphinx のドキュメント識別子。
        source: Markdown 原文を含む、変更可能な1要素リスト。
    """
    if docname != "index":
        return

    target = "en"
    badge_color = "red"
    href = "../en/index.html"
    destination = href
    if app.config.language == "en":
        target = "ja"
        badge_color = "yellow"
        href = "ja/index.html"
        destination = href
        if os.environ.get("FDMNES_DOCS_NESTED") == "1":
            destination = "../ja/index.html"

    badge = f"https://img.shields.io/badge/lang-{target}-{badge_color}.svg"
    markdown = f"[![{target}]({badge})]({href})"
    # Cross-edition pages are built separately from the current Sphinx tree.
    html = f'<a href="{destination}"><img src="{badge}" alt="{target}"></a>'
    source[0] = source[0].replace(markdown, html)


def setup(app):
    """言語切替リンクの生成処理を登録する。

    Args:
        app: 対象言語版を構成する Sphinx アプリケーション。
    """
    app.connect("source-read", _language_links)
