package listeners;

import intelligence.*;
import io.qameta.allure.Allure;
import io.qameta.allure.AllureLifecycle;
import io.qameta.allure.model.Status;
import io.qameta.allure.model.TestResult;
import org.testng.*;

import java.util.*;

public class ReleaseDecisionListener implements IExecutionListener, ITestListener {

    private static final Map<String, String> latestResults = new HashMap<>();

    @Override
    public void onTestSuccess(ITestResult result) {
        latestResults.put(result.getMethod().getMethodName(), "PASS");
    }

    @Override
    public void onTestFailure(ITestResult result) {
        latestResults.put(result.getMethod().getMethodName(), "FAIL");
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        latestResults.put(result.getMethod().getMethodName(), "SKIP");
    }

    @Override
    public void onExecutionFinish() {

        // 1) Load history
        Map<String, List<String>> history = TestHistoryManager.loadHistory();

        // 2) Update history with current run results
        TestHistoryManager.updateHistory(history, latestResults);

        // 3) Save history back
        TestHistoryManager.saveHistory(history);

        // 4) Detect flaky tests
        Map<String, Boolean> flakyTests = FlakyTestDetector.detectFlakyTests(history);

        // 5) Calculate risk scores (smart)
        Map<String, Integer> riskScores = RiskScoreCalculator.calculateRiskScores(
                latestResults,
                history,
                flakyTests
        );

        // 6) Final decision
        ReleaseDecisionEngine.Decision decision =
                ReleaseDecisionEngine.decideRelease(riskScores);

        // 7) Build Summary String (for console + Allure)
        StringBuilder summary = new StringBuilder();
        summary.append("===== RELEASE DECISION SUMMARY =====\n");

        riskScores.forEach((t, r) -> {
            boolean flaky = flakyTests.getOrDefault(t, false);
            summary.append(t)
                    .append(" → Risk: ")
                    .append(r)
                    .append(flaky ? " (FLAKY)" : "")
                    .append("\n");
        });

        summary.append("-----------------------------------\n");
        summary.append("FINAL DECISION → ").append(decision).append("\n");
        summary.append("===================================\n");

        // 8) Print to console
        System.out.println("\n" + summary);

        // 9)  Push Decision to Allure
        pushDecisionToAllure(summary.toString(), decision.toString());

        // 10) Optional CI gate
        if (decision == ReleaseDecisionEngine.Decision.NO_GO) {
            throw new RuntimeException(" Release blocked! FINAL DECISION = NO_GO");
        }
    }

    /**
     *  Adds Release Decision as a separate test case inside Allure report
     */
    private void pushDecisionToAllure(String decisionSummary, String finalDecision) {

        AllureLifecycle lifecycle = Allure.getLifecycle();

        String uuid = UUID.randomUUID().toString();

        Status status = finalDecision.equalsIgnoreCase("NO_GO")
                ? Status.FAILED
                : Status.PASSED;

        TestResult testResult = new TestResult()
                .setUuid(uuid)
                .setName("🚦 Release Decision")
                .setFullName("Release Decision Summary")
                .setStatus(status);

        lifecycle.scheduleTestCase(testResult);
        lifecycle.startTestCase(uuid);

        // Attachments
        Allure.addAttachment("Release Decision Summary", decisionSummary);
        Allure.addAttachment("FINAL DECISION", finalDecision);

        lifecycle.stopTestCase(uuid);
        lifecycle.writeTestCase(uuid);
    }
}
