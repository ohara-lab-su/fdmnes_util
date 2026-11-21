#!/usr/bin/env bash
set -euo pipefail

docs_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
build_dir="$docs_dir/_build"
python_bin="${PYTHON:-python3}"

if ! cmp -s "$docs_dir/index.md" "$docs_dir/en/index.md"; then
    printf '%s\n' 'Update docs/index.md and docs/en/index.md together.' >&2
    exit 1
fi

# Generate API sources in an isolated directory on every build.
source_dir="$(mktemp -d "${TMPDIR:-/tmp}/fdmnes-docs.XXXXXX")"
trap 'rm -rf "$source_dir"' EXIT

for language in en ja; do
    cp -R "$docs_dir/$language" "$source_dir/$language"
    title="Module index"
    if [[ "$language" == "ja" ]]; then
        title="モジュール一覧"
    fi
    "$python_bin" -m sphinx.ext.apidoc --separate --module-first \
        --doc-project "$title" -o "$source_dir/$language/api/generated" \
        "$docs_dir/../src/fdmnes_util"
done

# The site root is the same English edition as /en/. The link to /ja/
# is relative to each build so it also works on a local preview server.
FDMNES_DOCS_NESTED=0 "$python_bin" -m sphinx -W -b html \
    -c "$docs_dir" -d "$build_dir/doctrees/root" -D language=en \
    "$source_dir/en" "$build_dir/html"
FDMNES_DOCS_NESTED=1 "$python_bin" -m sphinx -W -b html \
    -c "$docs_dir" -d "$build_dir/doctrees/en" -D language=en \
    "$source_dir/en" "$build_dir/html/en"
"$python_bin" -m sphinx -W -b html \
    -c "$docs_dir" -d "$build_dir/doctrees/ja" -D language=ja \
    "$source_dir/ja" "$build_dir/html/ja"
