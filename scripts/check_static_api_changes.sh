#!/usr/bin/env bash
# Fails if any file under api/ has uncommitted changes (modified, added, or
# untracked), except under api/home/ or api/wisdom/ (those two rotate daily
# by design). Run after the randomizer/build scripts, before committing.
set -euo pipefail

changed=$(git status --porcelain -- api/ | sed -E 's/^...//' | grep -v '^api/home/' | grep -v '^api/wisdom/' || true)

if [ -n "$changed" ]; then
    echo "Unexpected static api changes outside home/wisdom:"
    echo "$changed"
    exit 1
fi

echo "ok: no unexpected changes outside api/home/ and api/wisdom/"
