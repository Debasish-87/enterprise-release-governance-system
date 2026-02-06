class ReleaseDecision:
    def __init__(self):
        self.issues = []

    def record_issue(self, issue):
        self.issues.append(issue)

    def is_release_allowed(self):
        return len(self.issues) == 0

    def summary(self):
        if self.is_release_allowed():
            return "RELEASE ALLOWED ✅"
        return f"RELEASE BLOCKED ❌ — Issues: {self.issues}"
