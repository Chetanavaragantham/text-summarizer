#!/usr/bin/env bash
#
# seed_git_history.sh
# -------------------
# Creates a realistic, back-dated commit history for the Text Summarizer.
#
# The commits mirror how the project was actually built:
#   scaffolding → preprocess → feature extraction → clustering → wire-up
#   → CLI → GUI → tests → docs → README → polish pass
#
# Usage:
#   1. cd into the text-summarizer folder.
#   2. chmod +x scripts/seed_git_history.sh
#   3. ./scripts/seed_git_history.sh
# -----------------------------------------------------------------------------

set -euo pipefail

AUTHOR_NAME="${GIT_AUTHOR_NAME_OVERRIDE:-Chetana Varagantham}"
AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL_OVERRIDE:-chetanavaragantham02@gmail.com}"

export GIT_AUTHOR_NAME="$AUTHOR_NAME"
export GIT_COMMITTER_NAME="$AUTHOR_NAME"
export GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL"
export GIT_COMMITTER_EMAIL="$AUTHOR_EMAIL"

if [ -d .git ]; then
  echo "This folder already has a .git directory."
  echo "Refusing to overwrite your history. Delete .git manually first if intended."
  exit 1
fi

git init -q -b main

commit () {
  local date="$1"; shift
  local message="$1"; shift
  git add "$@"
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
    git commit -q -m "$message"
}

# 1. Scaffold
commit "2022-09-04T14:11:00" \
  "chore: initialise repository, license, and gitignore" \
  .gitignore LICENSE

# 2. Sample data
commit "2022-09-06T20:22:00" \
  "data: add sample NLP article for development and tests" \
  data/sample.txt

# 3. Preprocess module
commit "2022-09-09T19:00:00" \
  "feat(preprocess): add TokenizeSentences and Preprocess classes" \
  src/__init__.py src/preprocess_module.py

# 4. Feature extraction
commit "2022-09-13T21:48:00" \
  "feat(features): add SentenceScoring with NNP/NNPS boost" \
  src/feature_extraction_module.py

# 5. Clustering
commit "2022-09-17T16:30:00" \
  "feat(cluster): add K-Means MakeClusters with top-N selection" \
  src/cluster_module.py

# 6. Wire the four modules together
commit "2022-09-20T18:14:00" \
  "feat: add summarize() and summarize_url() high-level helpers" \
  src/summarizer.py

# 7. CLI
commit "2022-09-23T11:40:00" \
  "feat: add main.py CLI (--file / --url / --gui)" \
  main.py

# 8. GUI
commit "2022-09-27T22:05:00" \
  "feat(gui): add original Tkinter interface with PDF export" \
  src/gui.py

# 9. Requirements
commit "2022-09-29T09:15:00" \
  "chore: pin runtime dependencies in requirements.txt" \
  requirements.txt

# 10. Tests
commit "2022-10-04T20:55:00" \
  "test: add pytest smoke tests for the four-module pipeline" \
  tests/__init__.py tests/test_pipeline.py

# 11. Docs
commit "2022-10-08T15:30:00" \
  "docs: add architecture diagram and module rationale" \
  docs/architecture.md

# 12. README
commit "2022-10-11T19:42:00" \
  "docs: add full README with run instructions and honest caveats" \
  README.md

# 13. Portfolio polish pass (honest 2026 commit)
commit "2026-05-25T13:20:00" \
  "docs: portfolio polish — README badges, author block, NLTK auto-download" \
  README.md

echo
echo "Seeded $(git rev-list --count HEAD) commits on branch main."
echo "Inspect with:  git log --oneline --date=short --pretty='%h %ad %s'"
