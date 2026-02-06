# Enterprise Release Governance System (ERGS)

ERGS is an **enterprise-style Release Governance Platform** built using **GitHub Actions**.

It automates:

- Automated Testing + Allure Reports  
- DevSecOps Security Scans (Gitleaks, Semgrep, Trivy)  
- SBOM Generation (Syft) + SBOM Vulnerability Scan (Grype)  
- Kubernetes Platform Quality Engineering (KPQE)  
- Single Consolidated Release Dashboard  
- Automated Final Release Decision Engine (GO / HOLD / NO-GO)  
- GitHub Pages Deployment for all reports  

---

## Live Reports Portal (GitHub Pages)

All pipeline outputs are deployed automatically to GitHub Pages.

### Main Portal
- [ERGS Reports Portal](https://debasish-87.github.io/enterprise-release-governance-system/)

### Reports Navigation

| Report Type | Live Link |
|-----------|----------|
| Release Dashboard | [Open Dashboard](https://debasish-87.github.io/enterprise-release-governance-system/dashboard/) |
| Allure Test Report | [Open Allure Report](https://debasish-87.github.io/enterprise-release-governance-system/allure/) |
| Security Reports | [Open Security Reports](https://debasish-87.github.io/enterprise-release-governance-system/security/) |
| SBOM Reports | [Open SBOM Reports](https://debasish-87.github.io/enterprise-release-governance-system/sbom/) |
| KPQE Platform Reports | [Open KPQE Reports](https://debasish-87.github.io/enterprise-release-governance-system/kpqe/) |
| Final Decision Output | [Open Final Decision](https://debasish-87.github.io/enterprise-release-governance-system/decision/) |
| Final Decision JSON | [final-decision.json](https://debasish-87.github.io/enterprise-release-governance-system/decision/final-decision.json) |

---

## Live Proof (Latest Successful Run Example)

Example successful run:

- Repo: `Debasish-87/enterprise-release-governance-system`
- Commit: `d6c797c89d6a6964b27e1f01dc2ae2f67762ac59`
- GitHub Actions Run:  
  [Open Run #21768128714](https://github.com/Debasish-87/enterprise-release-governance-system/actions/runs/21768128714)

---

## Why ERGS?

Modern releases require more than only “tests passed”.

ERGS enforces governance using **multi-layer validation** and generates a final decision:

- **GO** → safe to release  
- **HOLD** → manual review required  
- **NO-GO** → release blocked  

---

## Release Governance Pipeline (Layer-wise)

### Layer 1 — Application Testing (Allure)
Runs automated UI/API test suite and generates Allure reports.

**Outputs**
- Allure HTML report
- Test execution summary
- Testing intelligence summary (risk scoring)

---

### Layer 2 — Security Scans (DevSecOps)
Runs enterprise security scans:

- **Gitleaks** → Secrets detection  
- **Semgrep** → SAST scanning  
- **Trivy FS** → Repository vulnerability scanning  

**Outputs**
- `semgrep-report.json`
- `trivy-fs-report.json`
- `gitleaks-report.json` (optional)

---

### Layer 3 — SBOM + SBOM Vulnerability Scan
Generates SBOM and scans dependencies.

- **Syft** → generates SBOM (CycloneDX JSON)  
- **Grype** → scans SBOM for vulnerabilities  

**Outputs**
- `sbom-cyclonedx.json`
- `grype-sbom-report.json`

---

### Layer 4 — KPQE Platform Testing (Kubernetes)
Runs Kubernetes platform readiness + quality validation:

- Node readiness checks  
- Pod crashloop detection  
- Restart risk checks  
- Cluster health validation  

**Outputs**
- `kpqe-release-decision.txt`
- Cluster readiness reports (`nodes.json`, `pods.json`)

---

### Layer 5 — Consolidated Release Dashboard
A Python dashboard generator merges all signals into:

- One HTML dashboard  
- One JSON summary  

**Outputs**
- `index.html`
- `release-summary.json`

---

### Layer 6 — Final Decision Engine + GitHub Pages Deployment
Reads Layer 5 summary and generates:

- `final-decision.json`

Then deploys all reports into GitHub Pages:

- `/allure/`
- `/security/`
- `/sbom/`
- `/kpqe/`
- `/dashboard/`
- `/decision/`

---

## Final Decision Logic

ERGS generates the final decision using combined governance rules.

### GO
- Layer 1 tests passed  
- No High/Critical vulnerabilities in Trivy or Grype  
- KPQE decision = RELEASE ALLOWED  

### HOLD
- Tests passed but security issues exist  
  Example: Semgrep ERROR findings > 0  

### NO-GO
- Tests failed  
- Trivy High/Critical vulnerabilities found  
- Grype High/Critical vulnerabilities found  
- KPQE decision = RELEASE BLOCKED  

---

## Example Final Decision Output (Live JSON)

Final decision JSON is published here:

- [final-decision.json](https://debasish-87.github.io/enterprise-release-governance-system/decision/final-decision.json)

---

## Reports Generated

### Testing
- Allure HTML report  
- Test execution summary  

### Security
- Semgrep report (JSON)  
- Trivy FS report (JSON)  
- Gitleaks report (JSON)  

### SBOM
- CycloneDX SBOM JSON  
- Grype SBOM vulnerability report JSON  

### Platform Quality (KPQE)
- Node readiness  
- Crashloop detection  
- Restart risk checks  
- KPQE release decision  

### Consolidated Governance Outputs
- Release dashboard HTML  
- Release summary JSON  
- Final decision JSON  

---

## Project Structure

```bash
enterprise-release-governance-system/
│
├── .github/
│   └── workflows/
│       └── ci-release-governance.yml
│
├── application-testing/
│   ├── pom.xml
│   ├── regression.xml
│   ├── smoke.xml
│   ├── testng.xml
│   ├── src/
│   │   ├── main/java/
│   │   │   ├── base/
│   │   │   ├── intelligence/
│   │   │   ├── listeners/
│   │   │   ├── pages/
│   │   │   └── utils/
│   │   └── test/java/
│   │       └── tests/ui/
│   └── target/
│       ├── allure-results/
│       └── surefire-reports/
│
├── security-testing/
│   ├── run-gitleaks.sh
│   ├── run-semgrep.sh
│   ├── run-trivy.sh
│   └── reports/
│
├── sbom-testing/
│   ├── generate-sbom.sh
│   └── scan-sbom.sh
│
├── kpqe-platform-testing/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── quality_policy.md
│   ├── k8s/
│   ├── platform-tests/
│   └── quality_gates/
│
├── release-dashboard/
│   ├── generate-dashboard.py
│   └── requirements.txt
│
├── release-decision/
│   ├── final-decision.py
│   ├── requirements.txt
│   └── output/
│
└── .gitattributes
````

---

## Running Locally (Optional)

### Application Testing (Layer 1)

```bash
cd application-testing
mvn clean test
```

### Security Scans (Layer 2)

```bash
cd security-testing
bash run-semgrep.sh
bash run-trivy.sh
```

### SBOM Generation + Scan (Layer 3)

```bash
cd sbom-testing
bash generate-sbom.sh
bash scan-sbom.sh
```

### KPQE Platform Testing (Layer 4)

```bash
cd kpqe-platform-testing
pip install -r requirements.txt
pytest -q
```

---

## GitHub Actions Workflow

Main workflow file:

* `.github/workflows/ci-release-governance.yml`

This workflow produces:

* GitHub Actions artifacts
* GitHub Pages multi-report portal
* Automated final release decision

---

## Project Summary (Resume Ready)

Built an enterprise-grade Release Governance Platform that generates Allure reports, performs DevSecOps security scanning, creates SBOMs, scans SBOM vulnerabilities, validates Kubernetes readiness using KPQE, and enforces automated GO / HOLD / NO-GO release decisions using a consolidated dashboard deployed to GitHub Pages.

---

## Author

Debasish-87
GitHub: [https://github.com/Debasish-87](https://github.com/Debasish-87)

```

