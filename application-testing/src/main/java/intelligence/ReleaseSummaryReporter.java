package intelligence;

import io.qameta.allure.Allure;

import java.nio.charset.StandardCharsets;
import java.util.Map;

public class ReleaseSummaryReporter {

    public static void attachReleaseSummary(
            Map<String, Integer> riskScores,
            ReleaseDecisionEngine.Decision decision) {

        StringBuilder summary = new StringBuilder();

        summary.append("===== RELEASE DECISION SUMMARY =====\n\n");

        for (Map.Entry<String, Integer> entry : riskScores.entrySet()) {
            summary.append(entry.getKey())
                    .append(" → Risk: ")
                    .append(entry.getValue())
                    .append("\n");
        }

        summary.append("\n-----------------------------------\n");
        summary.append("FINAL DECISION → ").append(decision).append("\n");

        Allure.getLifecycle().addAttachment(
                "🚦 Release Decision Summary",
                "text/plain",
                ".txt",
                summary.toString().getBytes(StandardCharsets.UTF_8)
        );
    }
}
