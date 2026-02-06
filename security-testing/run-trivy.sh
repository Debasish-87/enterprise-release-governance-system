#!/usr/bin/env bash
set -euo pipefail

echo "=============================="
echo "🐳 Running Trivy (Vulnerability Scan)"
echo "=============================="

mkdir -p reports

TARGET_DIR="target-app"

# Check if target-app exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ ERROR: '$TARGET_DIR' folder not found!"
  echo "➡️ Make sure the workflow clones the target repo into '$TARGET_DIR' before running Trivy."
  exit 1
fi

# Install trivy if not present
if ! command -v trivy &> /dev/null; then
  echo "➡️ Installing Trivy..."
  sudo apt-get update -y
  sudo apt-get install -y wget apt-transport-https gnupg lsb-release
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
  sudo apt-get update -y
  sudo apt-get install -y trivy
fi

echo "➡️ Running Trivy filesystem scan on '$TARGET_DIR'..."

# Filesystem scan
trivy fs \
  --format json \
  --output reports/trivy-fs-report.json \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  "$TARGET_DIR"

echo "✅ Trivy scan completed"
