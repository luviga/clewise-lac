#!/bin/sh
# Rebuild every commit on main without email files (*.msg, *.eml, *.pst, *.ost, any case)
# and with the current .gitignore. Uses a temporary index; never touches the working tree.
set -e
TMPIDX="$(git rev-parse --git-dir)/rewrite.index"
NEWGI=$(git hash-object -w .gitignore)
OLDHEAD=$(git rev-parse refs/heads/main)
PARENT=""
for C in $(git rev-list --reverse "$OLDHEAD"); do
  rm -f "$TMPIDX"
  GIT_INDEX_FILE="$TMPIDX" git read-tree "$C"
  GIT_INDEX_FILE="$TMPIDX" git rm --cached --ignore-unmatch -q -- ':(icase)*.msg' ':(icase)*.eml' ':(icase)*.pst' ':(icase)*.ost'
  GIT_INDEX_FILE="$TMPIDX" git update-index --add --cacheinfo 100644,"$NEWGI",.gitignore
  T=$(GIT_INDEX_FILE="$TMPIDX" git write-tree)
  export GIT_AUTHOR_NAME="$(git log -1 --format=%an "$C")" GIT_AUTHOR_EMAIL="$(git log -1 --format=%ae "$C")" GIT_AUTHOR_DATE="$(git log -1 --format=%ad --date=raw "$C")"
  export GIT_COMMITTER_NAME="$(git log -1 --format=%cn "$C")" GIT_COMMITTER_EMAIL="$(git log -1 --format=%ce "$C")" GIT_COMMITTER_DATE="$(git log -1 --format=%cd --date=raw "$C")"
  if [ -z "$PARENT" ]; then N=$(git log -1 --format=%B "$C" | git commit-tree "$T"); else N=$(git log -1 --format=%B "$C" | git commit-tree "$T" -p "$PARENT"); fi
  echo "$C -> $N  $(git log -1 --format=%s "$C")"
  PARENT=$N
done
rm -f "$TMPIDX"
git update-ref -m "rewrite: drop email files" refs/heads/main "$PARENT" "$OLDHEAD"
git read-tree HEAD   # refresh the real index only; working tree untouched
