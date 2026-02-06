package intelligence;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RiskScoreCalculator {

    private static final Map<String, Integer> BASE_RISK = Map.of(
            "verifyHomePageLoads", 2,
            "verifyPredictionGenerated", 7
    );

    public static Map<String, Integer> calculateRiskScores(
            Map<String, String> latestResults,
            Map<String, List<String>> fullHistory,
            Map<String, Boolean> flakyTests) {

        Map<String, Integer> riskScores = new HashMap<>();

        for (Map.Entry<String, String> entry : latestResults.entrySet()) {

            String testName = entry.getKey();
            String status = entry.getValue();

            int risk = BASE_RISK.getOrDefault(testName, 3);

            // Failure increases risk
            if ("FAIL".equalsIgnoreCase(status)) {
                risk += 3;
            }

            // Flaky increases risk
            if (flakyTests.getOrDefault(testName, false)) {
                risk += 2;
            }

            // Multiple recent failures increases risk
            List<String> history = fullHistory.get(testName);
            if (history != null) {
                long failCount = history.stream().filter(x -> x.equalsIgnoreCase("FAIL")).count();
                if (failCount >= 3) {
                    risk += 2;
                }
            }

            riskScores.put(testName, Math.min(risk, 10));
        }

        return riskScores;
    }
}
