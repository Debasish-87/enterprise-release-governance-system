import os
import json
from datetime import datetime

# ----------------------------
# Helper functions
# ----------------------------

def safe_read_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def normalize_summary(summary: dict) -> dict:
    """
    Ensure the JSON always has:
      summary["layers"]["layer1"]["status"]
      summary["layers"]["layer2"]["semgrep"]["error"]
      summary["layers"]["layer2"]["trivy"]["high/critical"]
      summary["layers"]["layer3"]["grype"]["high/critical"]
      summary["layers"]["layer4"]["kpqe_decision"]
    """

    if not isinstance(summary, dict):
        summary = {}

    if "layers" not in summary or not isinstance(summary.get("layers"), dict):
        summary["layers"] = {}

    layers = summary["layers"]

    # Layer 1
    layers.setdefault("layer1", {})
    layers["layer1"].setdefault("status", "UNKNOWN")

    # Layer 2
    layers.setdefault("layer2", {})
    layers["layer2"].setdefault("semgrep", {})
    layers["layer2"]["semgrep"].setdefault("error", 0)

    layers["layer2"].setdefault("trivy", {})
    layers["layer2"]["trivy"].setdefault("high", 0)
    layers["layer2"]["trivy"].setdefault("critical", 0)

    # Layer 3
    layers.setdefault("layer3", {})
    layers["layer3"].setdefault("grype", {})
    layers["layer3"]["grype"].setdefault("high", 0)
    layers["layer3"]["grype"].setdefault("critical", 0)

    # Layer 4
    layers.setdefault("layer4", {})
    layers["layer4"].setdefault("kpqe_decision", "UNKNOWN")

    return summary


def decision_rule(summary):
    """
    FINAL DECISION RULE (simple enterprise logic)

    - If Layer1 FAIL -> NO-GO
    - If Semgrep ERROR > 0 -> HOLD
    - If Trivy HIGH/CRITICAL > 0 -> NO-GO
    - If Grype HIGH/CRITICAL > 0 -> NO-GO
    - If KPQE RELEASE BLOCKED -> NO-GO
    - Else -> GO
    """

    # Layer 1
    if summary["layers"]["layer1"]["status"] != "PASSED":
        return "NO-GO"

    # Layer 2 - Semgrep
    semgrep_errors = summary["layers"]["layer2"]["semgrep"]["error"]
    if semgrep_errors > 0:
        return "HOLD"

    # Trivy
    trivy_high = summary["layers"]["layer2"]["trivy"]["high"]
    trivy_critical = summary["layers"]["layer2"]["trivy"]["critical"]
    if trivy_high > 0 or trivy_critical > 0:
        return "NO-GO"

    # Layer 3 - Grype
    grype_high = summary["layers"]["layer3"]["grype"]["high"]
    grype_critical = summary["layers"]["layer3"]["grype"]["critical"]
    if grype_high > 0 or grype_critical > 0:
        return "NO-GO"

    # Layer 4 - KPQE
    kpqe_decision = summary["layers"]["layer4"]["kpqe_decision"]
    if kpqe_decision and "BLOCKED" in kpqe_decision.upper():
        return "NO-GO"

    return "GO"


# ----------------------------
# MAIN
# ----------------------------

def main():
    # Input paths (from Layer 5 output)
    possible_paths = [
        "release-decision/input/release-summary.json",
        "release-dashboard/output/release-summary.json",
        "release-dashboard/release-summary.json",
        "release-dashboard-artifact/release-summary.json",
        "release-dashboard-artifact/output/release-summary.json",
    ]

    dashboard_json = None
    used_path = None

    for p in possible_paths:
        dashboard_json = safe_read_json(p)
        if dashboard_json:
            used_path = p
            break

    if not dashboard_json:
        print("❌ ERROR: release-summary.json not found. Run Layer 5 first.")
        print("===== Searched paths =====")
        for p in possible_paths:
            print(" -", p)
        exit(1)

    # Normalize structure (prevents KeyError: layers)
    summary = normalize_summary(dashboard_json)

    final = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "repo": summary.get("repo"),
        "commit": summary.get("commit"),
        "run_id": summary.get("run_id"),
        "run_link": summary.get("run_link"),
        "final_decision": "UNKNOWN",
        "reasoning": []
    }

    # Apply rules
    decision = decision_rule(summary)
    final["final_decision"] = decision

    # Add reasoning
    final["reasoning"].append(f"Input Path Used = {used_path}")
    final["reasoning"].append(f"Layer1 status = {summary['layers']['layer1']['status']}")
    final["reasoning"].append(f"Semgrep ERROR = {summary['layers']['layer2']['semgrep']['error']}")
    final["reasoning"].append(
        f"Trivy HIGH/CRITICAL = {summary['layers']['layer2']['trivy']['high']}/{summary['layers']['layer2']['trivy']['critical']}"
    )
    final["reasoning"].append(
        f"Grype HIGH/CRITICAL = {summary['layers']['layer3']['grype']['high']}/{summary['layers']['layer3']['grype']['critical']}"
    )
    final["reasoning"].append(f"KPQE Decision = {summary['layers']['layer4']['kpqe_decision']}")

    # Save output
    os.makedirs("release-decision/output", exist_ok=True)

    with open("release-decision/output/final-decision.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    # Print nicely
    print("\n==============================")
    print("🚦 FINAL RELEASE DECISION (Layer 6)")
    print("==============================")
    print(f"Repo   : {final['repo']}")
    print(f"Commit : {final['commit']}")
    print(f"Run ID : {final['run_id']}")
    print(f"Decision: {final['final_decision']}")
    print("------------------------------")
    print("Reasoning:")
    for r in final["reasoning"]:
        print(f" - {r}")
    print("==============================\n")

    # If NO-GO -> fail pipeline
    if final["final_decision"] == "NO-GO":
        exit(1)

    # If HOLD -> fail pipeline too (recommended)
    if final["final_decision"] == "HOLD":
        exit(1)


if __name__ == "__main__":
    main()
