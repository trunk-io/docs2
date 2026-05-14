#!/usr/bin/env bash
set -euo pipefail

ASSETS_DIR="$(dirname "$0")/assets"
CONTENT_DIR="$(dirname "$0")"

# Collect all asset files with spaces
mapfile -d '' FILES < <(find "$ASSETS_DIR" -name "* *" -print0)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No files with spaces found."
  exit 0
fi

echo "Found ${#FILES[@]} file(s) with spaces. Processing..."

for OLD_PATH in "${FILES[@]}"; do
  OLD_NAME="$(basename "$OLD_PATH")"
  NEW_NAME="${OLD_NAME// /_}"

  if [[ "$OLD_NAME" == "$NEW_NAME" ]]; then
    continue
  fi

  NEW_PATH="$(dirname "$OLD_PATH")/$NEW_NAME"

  # Rename the file
  mv "$OLD_PATH" "$NEW_PATH"

  # Update references in all content files
  # Escape special chars for sed: ( ) . [ ]
  OLD_REF="/assets/${OLD_NAME}"
  NEW_REF="/assets/${NEW_NAME}"

  OLD_SED="$(printf '%s\n' "$OLD_REF" | sed 's/[][()\.]/\\&/g')"
  NEW_SED="$(printf '%s\n' "$NEW_REF" | sed 's/[&/\]/\\&/g')"

  while IFS= read -r CONTENT_FILE; do
    sed -i "s|${OLD_SED}|${NEW_SED}|g" "$CONTENT_FILE"
    echo "  Updated: $CONTENT_FILE"
  done < <(grep -rl --include="*.mdx" --include="*.md" --include="*.json" \
    "$OLD_REF" "$CONTENT_DIR" 2>/dev/null || true)

  echo "Renamed: $OLD_NAME -> $NEW_NAME"
done

echo "Done."
