#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🔒 Running Gitleaks (Secrets Scan)"
echo "=============================="

# Default scan folder = target-app
TARGET_DIR="${1:-target-app}"

# Reports folder (always inside security-testing)
REPORT_DIR="security-testing/reports"
mkdir -p "$REPORT_DIR"

# Check if target folder exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  echo "➡️ Make sure the workflow clones the target repo into '$TARGET_DIR' before running Gitleaks."
  exit 1
fi

# Install gitleaks if not present (stable method)
if ! command -v gitleaks &> /dev/null; then
  echo "➡️ Installing gitleaks..."

  # Download latest .deb package (Ubuntu runner friendly)
  curl -sSL -o gitleaks.deb \
    https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_8.18.2_linux_x64.deb

  sudo dpkg -i gitleaks.deb
  rm -f gitleaks.deb
fi

echo "➡️ Gitleaks Version:"
gitleaks version || true

echo "➡️ Scanning '$TARGET_DIR' for secrets..."

gitleaks detect \
  --source "$TARGET_DIR" \
  --report-format json \
  --report-path "$REPORT_DIR/gitleaks-report.json" \
  --verbose

echo "✅ Gitleaks scan completed successfully"
echo "📌 Report saved: $REPORT_DIR/gitleaks-report.json"
