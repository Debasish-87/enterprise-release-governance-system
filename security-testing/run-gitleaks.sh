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

# Install gitleaks if not present
if ! command -v gitleaks &> /dev/null; then
  echo "➡️ Installing gitleaks..."

  # Try .deb first (best for ubuntu-latest)
  curl -sSL -o gitleaks.deb \
    https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_8.18.2_linux_x64.deb || true

  if [ -f gitleaks.deb ]; then
    sudo dpkg -i gitleaks.deb || true
    rm -f gitleaks.deb
  fi

  # Fallback: tar.gz install
  if ! command -v gitleaks &> /dev/null; then
    echo "⚠️ .deb install failed, using tar.gz fallback..."

    curl -sSL -o gitleaks.tar.gz \
      https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_8.18.2_linux_x64.tar.gz

    tar -xzf gitleaks.tar.gz
    sudo mv gitleaks /usr/local/bin/gitleaks
    rm -f gitleaks.tar.gz
  fi
fi

echo "➡️ Gitleaks Version:"
gitleaks version || true

echo "➡️ Scanning '$TARGET_DIR' for secrets..."

# Run scan (doesn't require git history)
gitleaks detect \
  --source "$TARGET_DIR" \
  --report-format json \
  --report-path "$REPORT_DIR/gitleaks-report.json" \
  --verbose || true

echo "✅ Gitleaks scan completed"
echo "📌 Report saved: $REPORT_DIR/gitleaks-report.json"
