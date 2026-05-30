#!/bin/sh
set -e

cd /app

# Bind mount overwrites image deps — install into ./frontend/node_modules when needed.
if [ ! -d node_modules/nuxt ] || [ package-lock.json -nt node_modules/.package-lock.json ]; then
  echo "Installing npm dependencies..."
  npm ci
fi

# Regenerate .nuxt when missing (e.g. after clone or clean).
if [ ! -f .nuxt/nuxt.d.ts ] || [ -z "$(ls -A .nuxt/manifest/meta 2>/dev/null)" ]; then
  echo "Generating .nuxt (nuxt prepare)..."
  npx nuxt prepare
fi

exec "$@"
