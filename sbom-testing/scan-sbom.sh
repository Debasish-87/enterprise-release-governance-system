#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🛡️ Stage 3.5 - SBOM Vulnerability Scan"
echo "=============================="

REPORT_DIR="sbom-testing/reports"
SBOM_FILE="$REPORT_DIR/sbom-cyclonedx.json"

mkdir -p "$REPORT_DIR"

# Check SBOM exists
if [ ! -f "$SBOM_FILE" ]; then
  echo "❌ ERROR: SBOM file not found: $SBOM_FILE"
  echo "➡️ Run generate-sbom.sh first"
  exit 1
fi

# Install Trivy if not present
if ! command -v trivy &> /dev/null; then
  echo "➡️ Installing Trivy..."
  sudo apt-get update -y
  sudo apt-get install -y wget apt-transport-https gnupg lsb-release
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
  sudo apt-get update -y
  sudo apt-get install -y trivy
fi

echo "➡️ Trivy Version:"
trivy --version || true

echo "➡️ Scanning SBOM file: $SBOM_FILE"

trivy sbom \
  --format json \
  --output "$REPORT_DIR/sbom-vuln-report.json" \
  --severity HIGH,CRITICAL \
  --exit-code 0 \
  "$SBOM_FILE"

echo "✅ SBOM vulnerability scan completed"
echo "📌 Report saved: $REPORT_DIR/sbom-vuln-report.json"
