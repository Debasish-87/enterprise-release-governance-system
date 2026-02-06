#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🔒 Running Gitleaks (Secrets Scan)"
echo "=============================="

mkdir -p reports

TARGET_DIR="target-app"

# Check if target-app exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  echo "➡️ Make sure the workflow clones the target repo into '$TARGET_DIR' before running Gitleaks."
  exit 1
fi

# Install gitleaks if not present
if ! command -v gitleaks &> /dev/null; then
  echo "➡️ Installing gitleaks..."
  curl -sSL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64.tar.gz \
    | tar -xz
  sudo mv gitleaks /usr/local/bin/gitleaks
fi

echo "➡️ Scanning '$TARGET_DIR' for secrets..."
gitleaks detect \
  --source "$TARGET_DIR" \
  --report-format json \
  --report-path reports/gitleaks-report.json \
  --verbose

echo "✅ Gitleaks scan completed successfully"
