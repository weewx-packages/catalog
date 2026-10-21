#!/usr/bin/env bash
# Copy upstream refs without checking out or executing upstream code. The caller
# supplies push credentials; extension installers must never receive them.
set -euo pipefail

mirror_work=$(mktemp -d)
trap 'rm -rf "$mirror_work"' EXIT

git clone --bare "$1" "$mirror_work/upstream.git"
# Reject divergent branches and changed tags as one transaction. Keep refs that
# upstream deleted, so removing an upstream branch does not erase our copy.
git -C "$mirror_work/upstream.git" push --atomic "$2" \
    'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'
