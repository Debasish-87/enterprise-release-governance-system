import json
import os
from datetime import datetime


# -----------------------------
# Helpers
# -----------------------------
def safe_read_json(path, default=None):
    try:
        if not os.path.exists(path):
            return default if default is not None else {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def read_text(path, default=""):
    try:
        if not os.path.exists(path):
            return default
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return default


def html_escape(s: str) -> str:
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# -----------------------------
# GitHub Run Info
# -----------------------------
repo = os.getenv("GITHUB_REPOSITORY", "UNKNOWN")
sha = os.getenv("GITHUB_SHA", "UNKNOWN")
run_id = os.getenv("GITHUB_RUN_ID", "UNKNOWN")
run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
generated_time = datetime.utcnow().isoformat() + "Z"

owner = repo.split("/")[0] if "/" in repo else "UNKNOWN"
repo_name = repo.split("/")[1] if "/" in repo else "UNKNOWN"

# GitHub Pages root URL (repo pages)
pages_root_url = f"https://{owner}.github.io/{repo_name}/"

# In your Pages structure you have:
# /allure/
# /security/
# /sbom/
# /kpqe/
# /dashboard/
# /decision/
allure_pages_url = f"{pages_root_url}allure/"
security_pages_url = f"{pages_root_url}security/"
sbom_pages_url = f"{pages_root_url}sbom/"
kpqe_pages_url = f"{pages_root_url}kpqe/"
dashboard_pages_url = f"{pages_root_url}dashboard/"
decision_pages_url = f"{pages_root_url}decision/"


# ============================================================
# 1) ALLURE SUMMARY
# ============================================================
allure_summary_path = "application-testing/target/site/allure-report/widgets/summary.json"
allure_summary = safe_read_json(allure_summary_path, {})

stat = allure_summary.get("statistic", {}) or {}
allure_total = stat.get("total", 0) or 0
allure_passed = stat.get("passed", 0) or 0
allure_failed = stat.get("failed", 0) or 0
allure_broken = stat.get("broken", 0) or 0
allure_skipped = stat.get("skipped", 0) or 0

# FIX: If total == 0, it is FAILED (no tests ran)
if allure_total > 0 and allure_failed == 0 and allure_broken == 0:
    allure_status = "✅ PASSED"
else:
    allure_status = "❌ FAILED"


# ============================================================
# 2) SECURITY REPORTS
# ============================================================

# ---- GITLEAKS ----
gitleaks_path = "security-testing/reports/gitleaks-report.json"
gitleaks_json = safe_read_json(gitleaks_path, [])

gitleaks_findings = len(gitleaks_json) if isinstance(gitleaks_json, list) else 0
gitleaks_top = []

if isinstance(gitleaks_json, list):
    for item in gitleaks_json[:5]:
        desc = item.get("Description", "Unknown")
        file = item.get("File", "Unknown")
        rule = item.get("RuleID", "Unknown")
        gitleaks_top.append(f"{rule} | {file} | {desc}")


# ---- SEMGREP ----
semgrep_path = "security-testing/reports/semgrep-report.json"
semgrep_json = safe_read_json(semgrep_path, {})

semgrep_results = semgrep_json.get("results", []) or []
semgrep_findings = len(semgrep_results)

# FIX: Count severity from ALL results, not only first 10
semgrep_sev = {"ERROR": 0, "WARNING": 0, "INFO": 0}
semgrep_top = []

for r in semgrep_results:
    level = (r.get("extra", {}).get("severity") or "INFO").upper()
    if level not in semgrep_sev:
        semgrep_sev[level] = 0
    semgrep_sev[level] += 1

# Top findings list only 10
for r in semgrep_results[:10]:
    level = (r.get("extra", {}).get("severity") or "INFO").upper()
    path = r.get("path", "unknown")
    check_id = r.get("check_id", "unknown")
    msg = r.get("extra", {}).get("message", "no message")
    semgrep_top.append(f"{level} | {check_id} | {path} | {msg}")


# ---- TRIVY ----
# FIX: your artifact has trivy-fs-report.json (not trivy-report.json)
trivy_path = "security-testing/reports/trivy-fs-report.json"
trivy_json = safe_read_json(trivy_path, {})

trivy_findings = 0
trivy_sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
trivy_top = []

results = trivy_json.get("Results", []) or []

for res in results:
    vulns = res.get("Vulnerabilities", []) or []
    for v in vulns:
        trivy_findings += 1
        sev = (v.get("Severity") or "LOW").upper()
        if sev not in trivy_sev:
            trivy_sev[sev] = 0
        trivy_sev[sev] += 1

        if len(trivy_top) < 10:
            vid = v.get("VulnerabilityID", "UNKNOWN")
            pkg = v.get("PkgName", "UNKNOWN")
            inst = v.get("InstalledVersion", "")
            fixed = v.get("FixedVersion", "")
            trivy_top.append(f"{sev} | {vid} | {pkg} {inst} → {fixed}")


# ============================================================
# 3) SBOM + GRYPE REPORTS
# ============================================================

sbom_path = "sbom-testing/reports/sbom-cyclonedx.json"
sbom_json = safe_read_json(sbom_path, {})

components = sbom_json.get("components", []) or []
sbom_components = len(components)

sbom_top = []
for c in components[:10]:
    name = c.get("name", "unknown")
    version = c.get("version", "unknown")
    purl = c.get("purl", "")
    sbom_top.append(f"{name}:{version} {purl}")


grype_path = "sbom-testing/reports/grype-sbom-report.json"
grype_json = safe_read_json(grype_path, {})

matches = grype_json.get("matches", []) or []
grype_findings = len(matches)

grype_sev = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
grype_top = []

for m in matches:
    vuln = m.get("vulnerability", {}) or {}
    artifact = m.get("artifact", {}) or {}

    sev = (vuln.get("severity") or "UNKNOWN").upper()
    if sev not in grype_sev:
        grype_sev[sev] = 0
    grype_sev[sev] += 1

    if len(grype_top) < 10:
        vid = vuln.get("id", "UNKNOWN")
        pkg = artifact.get("name", "UNKNOWN")
        ver = artifact.get("version", "UNKNOWN")
        grype_top.append(f"{sev} | {vid} | {pkg}:{ver}")


# ============================================================
# 4) KPQE PLATFORM HEALTH DETAILS
# ============================================================

kpqe_decision_path = "kpqe-platform-testing/kpqe-release-decision.txt"
kpqe_text = read_text(kpqe_decision_path, "UNKNOWN")

if "RELEASE ALLOWED" in kpqe_text:
    kpqe_decision = "RELEASE ALLOWED ✅"
elif "RELEASE BLOCKED" in kpqe_text:
    kpqe_decision = "RELEASE BLOCKED ❌"
else:
    kpqe_decision = "UNKNOWN ⚠️"

nodes_json = safe_read_json("kpqe-platform-testing/reports/nodes.json", {})
pods_json = safe_read_json("kpqe-platform-testing/reports/pods.json", {})

# ---- Nodes ----
node_items = nodes_json.get("items", []) or []
total_nodes = len(node_items)
ready_nodes = 0
not_ready_nodes = []

for n in node_items:
    name = n.get("metadata", {}).get("name", "unknown")
    conditions = n.get("status", {}).get("conditions", []) or []
    for c in conditions:
        if c.get("type") == "Ready":
            if c.get("status") == "True":
                ready_nodes += 1
            else:
                not_ready_nodes.append(name)

# ---- Pods ----
pod_items = pods_json.get("items", []) or []
total_pods = len(pod_items)

crashloop_pods = []
restart_risk_pods = []

RESTART_THRESHOLD = 3

for p in pod_items:
    ns = p.get("metadata", {}).get("namespace", "unknown")
    name = p.get("metadata", {}).get("name", "unknown")

    statuses = p.get("status", {}).get("containerStatuses", []) or []
    for s in statuses:
        restart_count = s.get("restartCount", 0)
        state = s.get("state", {}) or {}

        waiting = state.get("waiting", {})
        if waiting and waiting.get("reason") == "CrashLoopBackOff":
            crashloop_pods.append(f"{ns}/{name}")

        if restart_count > RESTART_THRESHOLD:
            restart_risk_pods.append(f"{ns}/{name} (restarts={restart_count})")


# ============================================================
# 5) FINAL DECISION (MATCH LAYER 6)
# ============================================================

# Normalize Layer1 status for JSON
layer1_status = "PASSED" if ("PASSED" in allure_status) else "FAILED"

final_decision = "GO ✅"

# Rule 1: Layer1 must PASS
if layer1_status != "PASSED":
    final_decision = "NO-GO ❌"

# Rule 2: Semgrep ERROR -> HOLD
elif semgrep_sev.get("ERROR", 0) > 0:
    final_decision = "HOLD ⏸️"

# Rule 3: Trivy HIGH/CRITICAL -> NO-GO
elif trivy_sev.get("CRITICAL", 0) > 0 or trivy_sev.get("HIGH", 0) > 0:
    final_decision = "NO-GO ❌"

# Rule 4: Grype HIGH/CRITICAL -> NO-GO
elif grype_sev.get("CRITICAL", 0) > 0 or grype_sev.get("HIGH", 0) > 0:
    final_decision = "NO-GO ❌"

# Rule 5: KPQE blocked -> NO-GO
elif "BLOCKED" in kpqe_decision.upper():
    final_decision = "NO-GO ❌"


# ============================================================
# HTML
# ============================================================
def list_block(items):
    if not items:
        return "<p class='ok'>None ✅</p>"
    li = "".join([f"<li><code>{html_escape(x)}</code></li>" for x in items])
    return f"<ul>{li}</ul>"


html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Release Governance Dashboard</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 30px;
      background: #0b1220;
      color: white;
    }}
    .card {{
      background: #111a2e;
      padding: 18px;
      border-radius: 14px;
      margin-bottom: 16px;
      box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }}
    h1 {{ color: #00ffcc; }}
    h2 {{ margin-bottom: 8px; }}
    a {{ color: #00ffcc; }}
    .ok {{ color: #3cff00; font-weight: bold; }}
    .bad {{ color: #ff4d4d; font-weight: bold; }}
    .warn {{ color: #ffcc00; font-weight: bold; }}
    code {{
      background: #0b1220;
      padding: 3px 7px;
      border-radius: 6px;
      display: inline-block;
    }}
    ul {{
      margin-top: 8px;
      line-height: 1.6;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
  </style>
</head>
<body>

<h1>🚀 Release Governance Dashboard (Layer 5)</h1>

<div class="card">
  <h2>📌 Run Info</h2>
  <p><b>Repo:</b> {repo}</p>
  <p><b>Commit:</b> <code>{sha}</code></p>
  <p><b>Run ID:</b> {run_id}</p>
  <p><b>Run Link:</b> <a href="{run_url}" target="_blank">{run_url}</a></p>
  <p><b>Generated:</b> {generated_time}</p>
</div>

<div class="card">
  <h2>🧪 Layer 1 — Application Testing (Allure)</h2>
  <p><b>Status:</b> <span class="ok">{allure_status}</span></p>
  <p><b>Total:</b> {allure_total} | <b>Passed:</b> {allure_passed} | <b>Failed:</b> {allure_failed} | <b>Broken:</b> {allure_broken} | <b>Skipped:</b> {allure_skipped}</p>
  <p><b>Allure Report:</b> <a href="{allure_pages_url}" target="_blank">{allure_pages_url}</a></p>
</div>

<div class="card">
  <h2>🔐 Layer 2 — Security Scans</h2>

  <div class="grid">
    <div>
      <h3>🕵️ Gitleaks</h3>
      <p><b>Findings:</b> {gitleaks_findings}</p>
      <h4>Top Findings</h4>
      {list_block(gitleaks_top)}
    </div>

    <div>
      <h3>🧠 Semgrep</h3>
      <p><b>Findings:</b> {semgrep_findings}</p>
      <p>
        <b>ERROR:</b> {semgrep_sev.get("ERROR",0)} |
        <b>WARNING:</b> {semgrep_sev.get("WARNING",0)} |
        <b>INFO:</b> {semgrep_sev.get("INFO",0)}
      </p>
      <h4>Top Findings</h4>
      {list_block(semgrep_top)}
    </div>
  </div>

  <div style="margin-top:16px;">
    <h3>📦 Trivy</h3>
    <p><b>Total Vulnerabilities:</b> {trivy_findings}</p>
    <p>
      <b>CRITICAL:</b> {trivy_sev.get("CRITICAL",0)} |
      <b>HIGH:</b> {trivy_sev.get("HIGH",0)} |
      <b>MEDIUM:</b> {trivy_sev.get("MEDIUM",0)} |
      <b>LOW:</b> {trivy_sev.get("LOW",0)}
    </p>
    <h4>Top Vulnerabilities</h4>
    {list_block(trivy_top)}
  </div>
</div>

<div class="card">
  <h2>📦 Layer 3 — SBOM + SBOM Vulnerability Scan</h2>

  <p><b>SBOM Components:</b> {sbom_components}</p>
  <h4>Top Components</h4>
  {list_block(sbom_top)}

  <hr style="margin:18px 0; opacity:0.2;">

  <p><b>Grype Findings:</b> {grype_findings}</p>
  <p>
    <b>CRITICAL:</b> {grype_sev.get("CRITICAL",0)} |
    <b>HIGH:</b> {grype_sev.get("HIGH",0)} |
    <b>MEDIUM:</b> {grype_sev.get("MEDIUM",0)} |
    <b>LOW:</b> {grype_sev.get("LOW",0)} |
    <b>UNKNOWN:</b> {grype_sev.get("UNKNOWN",0)}
  </p>

  <h4>Top Vulnerabilities</h4>
  {list_block(grype_top)}
</div>

<div class="card">
  <h2>☸ Layer 4 — KPQE Platform Quality</h2>

  <p><b>Decision:</b> <span class="warn">{kpqe_decision}</span></p>

  <p><b>Nodes:</b> {ready_nodes}/{total_nodes} Ready</p>
  <p><b>Total Pods:</b> {total_pods}</p>

  <h4>NotReady Nodes</h4>
  {list_block(not_ready_nodes)}

  <h4>CrashLoopBackOff Pods</h4>
  {list_block(crashloop_pods)}

  <h4>Restart Risk Pods (restart > 3)</h4>
  {list_block(restart_risk_pods)}

  <h4>Raw KPQE Decision Output</h4>
  <pre style="background:#0b1220;padding:12px;border-radius:10px;">{html_escape(kpqe_text)}</pre>
</div>

<div class="card">
  <h2>🚦 Final Release Decision</h2>
  <p style="font-size:20px;"><b>{final_decision}</b></p>

  <p>
    <b>Dashboard:</b> <a href="{dashboard_pages_url}" target="_blank">{dashboard_pages_url}</a><br/>
    <b>Security:</b> <a href="{security_pages_url}" target="_blank">{security_pages_url}</a><br/>
    <b>SBOM:</b> <a href="{sbom_pages_url}" target="_blank">{sbom_pages_url}</a><br/>
    <b>KPQE:</b> <a href="{kpqe_pages_url}" target="_blank">{kpqe_pages_url}</a><br/>
    <b>Decision JSON:</b> <a href="{decision_pages_url}" target="_blank">{decision_pages_url}</a><br/>
  </p>
</div>

</body>
</html>
"""

os.makedirs("release-dashboard", exist_ok=True)
os.makedirs("release-dashboard/output", exist_ok=True)

# IMPORTANT:
# Pages uses /dashboard/ so index.html should also exist inside output/
with open("release-dashboard/output/index.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("release-dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Release dashboard generated:")
print(" - release-dashboard/index.html")
print(" - release-dashboard/output/index.html")


# ============================================================
# EXTRA: Generate release-summary.json (FOR LAYER 6)
# ============================================================

release_summary = {
    "repo": repo,
    "commit": sha,
    "run_id": run_id,
    "run_link": run_url,
    "generated_at": generated_time,

    "layers": {
        "layer1": {
            "status": layer1_status,
            "allure_pages_url": allure_pages_url,
            "total": allure_total,
            "passed": allure_passed,
            "failed": allure_failed,
            "broken": allure_broken,
            "skipped": allure_skipped
        },

        "layer2": {
            "gitleaks": {
                "findings": gitleaks_findings,
                "top_findings": gitleaks_top
            },
            "semgrep": {
                "findings": semgrep_findings,
                "error": semgrep_sev.get("ERROR", 0),
                "warning": semgrep_sev.get("WARNING", 0),
                "info": semgrep_sev.get("INFO", 0),
                "top_findings": semgrep_top
            },
            "trivy": {
                "findings": trivy_findings,
                "critical": trivy_sev.get("CRITICAL", 0),
                "high": trivy_sev.get("HIGH", 0),
                "medium": trivy_sev.get("MEDIUM", 0),
                "low": trivy_sev.get("LOW", 0),
                "top_vulnerabilities": trivy_top
            }
        },

        "layer3": {
            "sbom_components": sbom_components,
            "top_components": sbom_top,
            "grype": {
                "findings": grype_findings,
                "critical": grype_sev.get("CRITICAL", 0),
                "high": grype_sev.get("HIGH", 0),
                "medium": grype_sev.get("MEDIUM", 0),
                "low": grype_sev.get("LOW", 0),
                "unknown": grype_sev.get("UNKNOWN", 0),
                "top_vulnerabilities": grype_top
            }
        },

        "layer4": {
            "kpqe_decision": kpqe_decision,
            "nodes_total": total_nodes,
            "nodes_ready": ready_nodes,
            "pods_total": total_pods,
            "not_ready_nodes": not_ready_nodes,
            "crashloop_pods": crashloop_pods,
            "restart_risk_pods": restart_risk_pods,
            "raw_kpqe_output": kpqe_text
        }
    }
}

with open("release-dashboard/output/release-summary.json", "w", encoding="utf-8") as f:
    json.dump(release_summary, f, indent=2)

print("✅ Release summary JSON generated: release-dashboard/output/release-summary.json")
