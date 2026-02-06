# Intelligent Release Governance System (IRGS)

IRGS is an **enterprise-style DevSecOps + Quality Engineering Release Governance Platform** built using **GitHub Actions**.

It automates:

- Automated Testing + Allure Reports  
- Security Scans (Gitleaks, Semgrep, Trivy)  
- SBOM Generation (Syft) + SBOM Vulnerability Scan (Grype)  
- Kubernetes Platform Quality Engineering (KPQE)  
- Single Consolidated Release Dashboard  
- Automated Final Release Decision Engine (GO / HOLD / NO-GO)  
- GitHub Pages Deployment for all reports  

---

## Live Reports (GitHub Pages)

Once the pipeline runs successfully, reports are available here:

- Main Portal (Root)  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/`

- Allure Report  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/allure/`

- Security Reports  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/security/`

- SBOM Reports  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/sbom/`

- KPQE Platform Reports  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/kpqe/`

- Release Dashboard  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/dashboard/`

- Final Decision Output  
  `https://debasish-87.github.io/Intelligent-Release-Governance-System/decision/`

---

## Why IRGS?

Modern software releases require more than just "tests passed".

IRGS combines **testing + security + platform readiness** into one single pipeline and produces a final release decision:

- GO → Safe to release  
- HOLD → Needs manual review  
- NO-GO → Block release  

---

## Release Governance Pipeline (Layer-wise)

### Layer 1 — Application Testing + Allure
Runs automated UI/API test suite and generates Allure reports.

**Outputs**
- Allure Report (HTML)
- Test results
- Risk scoring / intelligence summary

---

### Layer 2 — Security Scans (DevSecOps)
Performs security checks using:

- Gitleaks → Secrets scanning  
- Semgrep → SAST scanning  
- Trivy FS → Repo vulnerability scan  

**Outputs**
- `semgrep-report.json`
- `trivy-fs-report.json`
- `gitleaks-report.json` (if enabled)

---

### Layer 3 — SBOM + SBOM Vulnerability Scan
Generates SBOM and scans dependencies.

- Syft → generates SBOM (CycloneDX JSON)
- Grype → scans SBOM for vulnerabilities

**Outputs**
- `sbom-cyclonedx.json`
- `sbom-vuln-report.json`

---

### Layer 4 — KPQE Platform Testing (Kubernetes)
Runs Kubernetes platform readiness + quality checks:

- Node readiness
- Pod crashloops
- Restart risk detection
- Cluster health checks

**Outputs**
- `kpqe-release-decision.txt`
- KPQE raw reports folder

---

### Layer 5 — Single Consolidated Release Dashboard
A Python dashboard generator merges all signals into:

- One HTML dashboard
- One JSON summary

**Outputs**
- `index.html`
- `release-summary.json`

---

### Layer 6 — Final Release Decision Engine + GitHub Pages Deploy
Final decision engine reads the Layer 5 summary and generates:

- `final-decision.json`

Then it deploys everything to GitHub Pages under folders:

- `/allure/`
- `/security/`
- `/sbom/`
- `/kpqe/`
- `/dashboard/`
- `/decision/`

---

## Final Decision Logic

IRGS produces final release decision based on combined signals:

### GO
- All tests passed
- No High/Critical vulnerabilities
- KPQE decision = RELEASE ALLOWED

### HOLD
- Tests passed but security warnings/errors exist  
  Example: Semgrep errors/warnings found

### NO-GO
- Critical vulnerabilities found  
- KPQE fails  
- Release gates violated

---

## Reports Generated

### Testing
- Allure HTML report
- Test execution summary

### Security
- Semgrep JSON
- Trivy JSON
- Gitleaks JSON (optional)

### SBOM
- CycloneDX SBOM JSON
- SBOM vulnerability scan JSON

### Platform Quality (KPQE)
- Node readiness report
- Crashloop detection
- Restart risk checks

### Consolidated Outputs
- Release dashboard (HTML)
- Release summary JSON
- Final decision JSON

---

## Project Structure

```bash
Intelligent-Release-Governance-System/
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

## How to Run Locally (Optional)

### 1) Run Application Testing (Layer 1)

```bash
cd application-testing
mvn clean test
```

### 2) Run Security Scans (Layer 2)

```bash
cd security-testing
bash run-semgrep.sh
bash run-trivy.sh
```

### 3) Generate SBOM (Layer 3)

```bash
cd sbom-testing
bash generate-sbom.sh
bash scan-sbom.sh
```

### 4) Run KPQE Platform Testing (Layer 4)

```bash
cd kpqe-platform-testing
pip install -r requirements.txt
pytest -q
```

---

## GitHub Actions Workflow

Main pipeline file:

`.github/workflows/ci-release-governance.yml`

It produces:

* GitHub Actions artifacts
* GitHub Pages reports
* Final Release Decision

---

## Project Summary (Resume Ready)

Built an end-to-end Release Governance Platform that generates Allure reports, performs DevSecOps security scanning, creates SBOMs, scans SBOM vulnerabilities, validates Kubernetes readiness using KPQE, and enforces automated GO / HOLD / NO-GO release decisions using a consolidated dashboard deployed to GitHub Pages.

---

## Author

Debasish-87
GitHub: `https://github.com/Debasish-87`

```
