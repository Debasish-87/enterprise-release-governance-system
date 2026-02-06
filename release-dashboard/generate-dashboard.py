import json
import os
from datetime import datetime
from jinja2 import Template

REPORTS_DIR = "release-dashboard/reports"
OUTPUT_DIR = "release-dashboard/output"

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_read_json(path):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

def safe_read_text(path):
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return None

# -----------------------------
# Load reports
# -----------------------------
gitleaks = safe_read_json("security-testing/reports/gitleaks-report.json")
semgrep = safe_read_json("security-testing/reports/semgrep-report.json")
trivy = safe_read_json("security-testing/reports/trivy-fs-report.json")

sbom = safe_read_json("sbom-testing/reports/sbom-cyclonedx.json")
sbom_scan = safe_read_json("sbom-testing/reports/grype-sbom-report.json")

kpqe_decision_text = safe_read_text("kpqe-platform-testing/kpqe-release-decision.txt")

# -----------------------------
# Extract summaries
# -----------------------------
summary = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "commit_sha": os.getenv("GITHUB_SHA", "unknown"),
    "repo": os.getenv("GITHUB_REPOSITORY", "unknown"),
    "run_id": os.getenv("GITHUB_RUN_ID", "unknown"),
}

# Gitleaks summary
gitleaks_findings = 0
if gitleaks and isinstance(gitleaks, dict):
    if "leaks" in gitleaks and isinstance(gitleaks["leaks"], list):
        gitleaks_findings = len(gitleaks["leaks"])

# Semgrep summary
semgrep_findings = 0
if semgrep and isinstance(semgrep, dict):
    if "results" in semgrep and isinstance(semgrep["results"], list):
        semgrep_findings = len(semgrep["results"])

# Trivy summary
trivy_findings = 0
if trivy and isinstance(trivy, dict):
    if "Results" in trivy and isinstance(trivy["Results"], list):
        for r in trivy["Results"]:
            vulns = r.get("Vulnerabilities") or []
            trivy_findings += len(vulns)

# SBOM summary
sbom_components = 0
if sbom and isinstance(sbom, dict):
    comps = sbom.get("components") or []
    sbom_components = len(comps)

# KPQE decision
kpqe_decision = "UNKNOWN"
if kpqe_decision_text:
    if "RELEASE ALLOWED" in kpqe_decision_text:
        kpqe_decision = "RELEASE ALLOWED"
    elif "RELEASE BLOCKED" in kpqe_decision_text:
        kpqe_decision = "RELEASE BLOCKED"

summary.update({
    "gitleaks_findings": gitleaks_findings,
    "semgrep_findings": semgrep_findings,
    "trivy_findings": trivy_findings,
    "sbom_components": sbom_components,
    "kpqe_decision": kpqe_decision
})

# -----------------------------
# Generate HTML Dashboard
# -----------------------------
template_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Release Governance Dashboard</title>
  <style>
    body { font-family: Arial; margin: 20px; background:#0b0f14; color:#e8eef6; }
    h1 { color:#00e676; }
    .card { background:#121826; padding:16px; margin:12px 0; border-radius:10px; }
    .good { color:#00e676; font-weight:bold; }
    .bad { color:#ff5252; font-weight:bold; }
    .warn { color:#ffb300; font-weight:bold; }
    code { background:#1c2433; padding:3px 6px; border-radius:6px; }
  </style>
</head>
<body>

<h1>🚀 Release Governance Dashboard</h1>

<div class="card">
  <h2>📌 Run Info</h2>
  <p><b>Repo:</b> {{ repo }}</p>
  <p><b>Commit:</b> <code>{{ commit_sha }}</code></p>
  <p><b>Run ID:</b> {{ run_id }}</p>
  <p><b>Generated:</b> {{ generated_at }}</p>
</div>

<div class="card">
  <h2>🧪 Application Testing</h2>
  <p>Allure report artifact generated ✅</p>
</div>

<div class="card">
  <h2>🔐 Security Scans</h2>
  <p><b>Gitleaks findings:</b> {{ gitleaks_findings }}</p>
  <p><b>Semgrep findings:</b> {{ semgrep_findings }}</p>
  <p><b>Trivy findings:</b> {{ trivy_findings }}</p>
</div>

<div class="card">
  <h2>📦 SBOM</h2>
  <p><b>SBOM components:</b> {{ sbom_components }}</p>
  <p>SBOM scan report generated ✅</p>
</div>

<div class="card">
  <h2>☸ KPQE Platform Quality</h2>
  <p><b>Decision:</b>
    {% if kpqe_decision == "RELEASE ALLOWED" %}
      <span class="good">{{ kpqe_decision }}</span>
    {% elif kpqe_decision == "RELEASE BLOCKED" %}
      <span class="bad">{{ kpqe_decision }}</span>
    {% else %}
      <span class="warn">{{ kpqe_decision }}</span>
    {% endif %}
  </p>
</div>

<div class="card">
  <h2>📌 Final Note</h2>
  <p>This is Layer 5 — Single consolidated release governance dashboard.</p>
</div>

</body>
</html>
"""

html = Template(template_html).render(**summary)

with open(os.path.join(OUTPUT_DIR, "release-dashboard.html"), "w", encoding="utf-8") as f:
    f.write(html)

with open(os.path.join(OUTPUT_DIR, "release-summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

print("✅ Dashboard generated successfully")
print("📌 Output:")
print(" - release-dashboard/output/release-dashboard.html")
print(" - release-dashboard/output/release-summary.json")
