package intelligence;

import java.util.*;

public class FlakyTestDetector {

    private static final int MIN_RUNS = 3;
    private static final int FAIL_THRESHOLD = 2;

    public static boolean isFlaky(List<String> history) {

        if (history == null || history.size() < MIN_RUNS) {
            return false;
        }

        int passCount = 0;
        int failCount = 0;

        for (String r : history) {
            if ("PASS".equalsIgnoreCase(r)) passCount++;
            if ("FAIL".equalsIgnoreCase(r)) failCount++;
        }

        // Flaky = has both PASS and FAIL + fails >= threshold
        return passCount >= 1 && failCount >= FAIL_THRESHOLD;
    }

    public static Map<String, Boolean> detectFlakyTests(Map<String, List<String>> fullHistory) {

        Map<String, Boolean> flakyMap = new HashMap<>();

        for (Map.Entry<String, List<String>> entry : fullHistory.entrySet()) {
            flakyMap.put(entry.getKey(), isFlaky(entry.getValue()));
        }

        return flakyMap;
    }
}
