#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🔍 Running Semgrep (SAST Scan)"
echo "=============================="

# Default scan folder = target-app
TARGET_DIR="${1:-target-app}"

# Reports folder (always inside security-testing)
REPORT_DIR="security-testing/reports"
mkdir -p "$REPORT_DIR"

# Check if target folder exists
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

echo "➡️ Semgrep Version:"
semgrep --version || true

echo "➡️ Running Semgrep scan on '$TARGET_DIR'..."

# Run scan
semgrep \
  --config=auto \
  --json \
  --output "$REPORT_DIR/semgrep-report.json" \
  "$TARGET_DIR" || true

echo "✅ Semgrep scan completed"
echo "📌 Report saved: $REPORT_DIR/semgrep-report.json"
