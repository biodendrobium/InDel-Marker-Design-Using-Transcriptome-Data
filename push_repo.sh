#!/usr/bin/env bash
# Usage: ./push_repo.sh "add pipeline docs and scripts"
set -euo pipefail

REPO_DIR="${1:-.}"
MSG="${2:-update: add pipeline docs and scripts}"

# Create layout
mkdir -p scripts data results db

# Move scripts if needed
# mv step1.extract_indel.py scripts/
# mv step2.150bp.py scripts/
# mv step3.primerdesign.py scripts/
# mv step4.extract-primer.py scripts/
# mv step5.blast_compare.py scripts/
# mv step6.final.py scripts/

git add .
git commit -m "$MSG"
git push origin main  # or 'master' if your repo uses that
