#!/usr/bin/env bash
# One-step deploy: build locally as a sanity check, then commit + push to main.
# Pushing to main triggers .github/workflows/deploy.yml, which builds again in
# CI and deploys dist/ to Cloudflare Pages. Nothing here talks to Cloudflare
# directly — this script's only job is to get a known-good commit onto main.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ -n "$(git status --porcelain)" ]; then
  echo "==> Changes to deploy:"
  git status --short
  echo
else
  echo "Nothing to commit — working tree is clean."
fi

branch=$(git branch --show-current)
if [ "$branch" != "main" ]; then
  echo "::error:: on branch '$branch', not 'main'. Switch to main before deploying." >&2
  exit 1
fi

echo "==> Installing deps"
npm ci

echo "==> Build check (astro build + pagefind)"
npm run build

if [ -n "$(git status --porcelain)" ]; then
  msg="${1:-Deploy: $(date '+%Y-%m-%d %H:%M')}"
  echo "==> Committing: $msg"
  git add -A
  git commit -m "$msg"
fi

echo "==> Pushing to origin/main (triggers Cloudflare Pages deploy)"
git push origin main

echo "==> Done. Watch the deploy: https://github.com/aathif394/ajascollege/actions"
