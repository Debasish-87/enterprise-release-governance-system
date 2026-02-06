#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "📦 Stage 3.5 - Generate SBOM"
echo "=============================="

TARGET_DIR="${1:-target-app}"

REPORT_DIR="sbom-testing/reports"
mkdir -p "$REPORT_DIR"

# Check target folder exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  exit 1
fi

# Install Syft if not present
if ! command -v syft &> /dev/null; then
  echo "➡️ Installing Syft (SBOM generator)..."
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
fi

echo "➡️ Syft Version:"
syft version || true

echo "➡️ Generating SBOM for '$TARGET_DIR'..."

syft dir:"$TARGET_DIR" \
  -o cyclonedx-json \
  > "$REPORT_DIR/sbom-cyclonedx.json"

echo "✅ SBOM generated successfully"
echo "📌 SBOM saved: $REPORT_DIR/sbom-cyclonedx.json"
