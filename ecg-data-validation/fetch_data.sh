#!/usr/bin/env bash
# Download the PTB records listed in records.txt into data/ (header + signal files).
set -euo pipefail
cd "$(dirname "$0")"
BASE=https://physionet.org/files/ptbdb/1.0.0
grep -v '^#' records.txt | awk 'NF {print $1}' | while read -r rec; do
    mkdir -p "data/$(dirname "$rec")"
    for ext in hea dat xyz; do
        [ -f "data/$rec.$ext" ] || curl -sfo "data/$rec.$ext" "$BASE/$rec.$ext"
    done
    echo "$rec"
done
