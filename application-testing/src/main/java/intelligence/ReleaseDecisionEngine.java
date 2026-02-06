package intelligence;

import java.util.Map;

public class ReleaseDecisionEngine {

    public enum Decision {
        GO,
        HOLD,
        NO_GO
    }

    /**
     * Strong Rules (Interview Ready):
     *
     * 1) Any Critical test risk >= 7  -> NO_GO
     * 2) Any test risk >= 9          -> NO_GO
     * 3) Average risk >= 5           -> HOLD
     * 4) Otherwise                   -> GO
     */
    public static Decision decideRelease(Map<String, Integer> riskScores) {

        // Hard blockers
        for (Map.Entry<String, Integer> entry : riskScores.entrySet()) {

            String testName = entry.getKey();
            int risk = entry.getValue();

            // Critical tests are release blockers
            if (testName.toLowerCase().contains("critical") && risk >= 7) {
                return Decision.NO_GO;
            }

            // Any very high risk blocks release
            if (risk >= 9) {
                return Decision.NO_GO;
            }
        }

        // Average risk check
        double avgRisk = riskScores.values().stream()
                .mapToInt(Integer::intValue)
                .average()
                .orElse(0);

        if (avgRisk >= 5) {
            return Decision.HOLD;
        }

        return Decision.GO;
    }
}
