#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🔍 Running Semgrep (SAST Scan)"
echo "=============================="

mkdir -p reports

TARGET_DIR="target-app"

# Check if target-app exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  echo "➡️ Make sure the workflow clones the target repo into '$TARGET_DIR' before running Semgrep."
  exit 1
fi

# Install semgrep if not present
if ! command -v semgrep &> /dev/null; then
  echo "➡️ Installing semgrep..."
  python3 -m pip install --upgrade pip
  pip install semgrep
fi

echo "➡️ Running Semgrep scan on '$TARGET_DIR'..."
semgrep \
  --config=auto \
  --json \
  --output reports/semgrep-report.json \
  "$TARGET_DIR"

echo "✅ Semgrep scan completed"
