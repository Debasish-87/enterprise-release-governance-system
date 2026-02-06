#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🐳 Running Trivy (Vulnerability Scan)"
echo "=============================="

# Default scan folder = target-app
TARGET_DIR="${1:-target-app}"

# Reports folder (always inside security-testing)
REPORT_DIR="security-testing/reports"
mkdir -p "$REPORT_DIR"

# Check if target folder exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  echo "➡️ Make sure the workflow clones the target repo into '$TARGET_DIR' before running Trivy."
  exit 1
fi

# Install trivy if not present (GitHub Actions Ubuntu runner safe method)
if ! command -v trivy &> /dev/null; then
  echo "➡️ Installing Trivy..."

  sudo apt-get update -y
  sudo apt-get install -y wget gnupg lsb-release apt-transport-https

  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key \
    | gpg --dearmor \
    | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null

  echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" \
    | sudo tee /etc/apt/sources.list.d/trivy.list

  sudo apt-get update -y
  sudo apt-get install -y trivy
fi

echo "➡️ Trivy Version:"
trivy --version || true

echo "➡️ Running Trivy filesystem scan on '$TARGET_DIR'..."

# Run scan (HIGH + CRITICAL)
trivy fs \
  --format json \
  --output "$REPORT_DIR/trivy-fs-report.json" \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  "$TARGET_DIR" || true

echo "✅ Trivy scan completed"
echo "📌 Report saved: $REPORT_DIR/trivy-fs-report.json"
