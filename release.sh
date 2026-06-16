#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# release.sh — create and push a version tag to trigger GitHub Pages deployment
#
# Usage:
#   ./release.sh             auto patch  v0.1.0 → v0.1.1  (default, no argument needed)
#   ./release.sh patch       v0.1.0 → v0.1.1
#   ./release.sh minor       v0.1.0 → v0.2.0
#   ./release.sh major       v0.1.0 → v1.0.0
#   ./release.sh v0.2.0      use exact version
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Helpers ───────────────────────────────────────────────────────────────────

usage() {
  echo "Usage: $0 patch|minor|major|vX.Y.Z" >&2
  exit 1
}

err() {
  echo "Error: $*" >&2
  exit 1
}

confirm() {
  # confirm <prompt>  — returns 0 if user enters y/Y, 1 otherwise
  printf "%s [y/N] " "$1"
  read -r _reply
  [[ "$_reply" =~ ^[Yy]$ ]]
}

# ── Argument check ─────────────────────────────────────────────────────────────

# No argument → default to patch
ARG="${1:-patch}"

# ── Git repo check ────────────────────────────────────────────────────────────

git rev-parse --git-dir &>/dev/null || err "Not inside a git repository."

# ── Branch check ──────────────────────────────────────────────────────────────

BRANCH=$(git rev-parse --abbrev-ref HEAD)
[[ "$BRANCH" == "main" ]] || err "Must be on the 'main' branch (currently on '$BRANCH')."

# ── Remote check ──────────────────────────────────────────────────────────────

git remote get-url origin &>/dev/null || err "No remote 'origin' found. Add one with: git remote add origin <url>"

# ── Working tree check ────────────────────────────────────────────────────────

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Warning: You have uncommitted changes."
  git status --short
  echo ""
  if confirm "Auto-commit all changes with 'git add . && git commit -m \"docs: update site content\"'?"; then
    git add .
    git commit -m "docs: update site content"
    echo "Changes committed."
    echo ""
  else
    echo "Release cancelled. Commit or stash your changes first, then re-run."
    exit 1
  fi
fi

# ── Latest tag ────────────────────────────────────────────────────────────────

LATEST=$(git tag --list 'v[0-9]*.[0-9]*.[0-9]*' | sort -V | tail -n 1)
if [[ -z "$LATEST" ]]; then
  LATEST="v0.0.0"
  echo "No existing tags found. Starting from $LATEST."
fi

# Parse components
if [[ "$LATEST" =~ ^v([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
  MAJOR="${BASH_REMATCH[1]}"
  MINOR="${BASH_REMATCH[2]}"
  PATCH="${BASH_REMATCH[3]}"
else
  err "Could not parse semver from latest tag '$LATEST'. Expected vX.Y.Z."
fi

# ── Compute next version ──────────────────────────────────────────────────────

case "$ARG" in
  patch)
    NEXT="v${MAJOR}.${MINOR}.$((PATCH + 1))"
    ;;
  minor)
    NEXT="v${MAJOR}.$((MINOR + 1)).0"
    ;;
  major)
    NEXT="v$((MAJOR + 1)).0.0"
    ;;
  v*)
    # Explicit version — validate format
    [[ "$ARG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] \
      || err "Version '$ARG' must be in the format vX.Y.Z (e.g. v0.2.0)."
    NEXT="$ARG"
    ;;
  *)
    err "Unknown argument '$ARG'. Use patch, minor, major, or vX.Y.Z."
    ;;
esac

# ── Duplicate tag check ───────────────────────────────────────────────────────

if git tag --list | grep -qx "$NEXT"; then
  err "Tag '$NEXT' already exists. Choose a different version or delete the existing tag first."
fi

# ── Confirm release ───────────────────────────────────────────────────────────

echo "Current latest version: $LATEST"
echo "Next version:           $NEXT"
echo ""

confirm "Release $NEXT?" || { echo "Release cancelled."; exit 0; }

echo ""

# ── Push main ─────────────────────────────────────────────────────────────────

echo "Pushing main to origin..."
git push origin main

# ── Tag and push ──────────────────────────────────────────────────────────────

echo "Creating tag $NEXT..."
git tag "$NEXT"

echo "Pushing tag $NEXT to origin..."
git push origin "$NEXT"

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
echo "Release complete. Tag $NEXT pushed."
echo "GitHub Pages deployment should start automatically."
echo "Track the workflow at: https://github.com/ytzc/larp-script-archive/actions"
