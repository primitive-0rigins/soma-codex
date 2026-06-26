#!/usr/bin/env bash
# Usage: ./render_svgs.sh name1 name2 ...  (renders img/<name>.svg -> img/<name>.png via LibreOffice)
set -e
cd "$(dirname "$0")"
tmp=$(mktemp -d)
for n in "$@"; do cp "img/$n.svg" "$tmp/"; done
soffice --headless --convert-to png --outdir "$tmp" "$tmp"/*.svg >/dev/null 2>&1
for n in "$@"; do cp "$tmp/$n.png" "img/$n.png"; done
rm -rf "$tmp"
ls -l img/*.png | awk '{print $5, $9}'
