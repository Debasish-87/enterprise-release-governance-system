package intelligence;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.*;

public class TestHistoryManager {

    private static final String HISTORY_FILE = "history/test-history.json";
    private static final ObjectMapper mapper = new ObjectMapper();

    public static Map<String, List<String>> loadHistory() {

        try {
            File file = new File(HISTORY_FILE);

            if (!file.exists()) {
                return new HashMap<>();
            }

            return mapper.readValue(file, new TypeReference<>() {});
        } catch (Exception e) {
            System.out.println("⚠ Failed to load history: " + e.getMessage());
            return new HashMap<>();
        }
    }

    public static void saveHistory(Map<String, List<String>> history) {

        try {
            File file = new File(HISTORY_FILE);

            // Ensure folder exists
            file.getParentFile().mkdirs();

            mapper.writerWithDefaultPrettyPrinter().writeValue(file, history);

        } catch (Exception e) {
            System.out.println("⚠ Failed to save history: " + e.getMessage());
        }
    }

    public static void updateHistory(Map<String, List<String>> history, Map<String, String> latestResults) {

        for (Map.Entry<String, String> entry : latestResults.entrySet()) {

            String testName = entry.getKey();
            String result = entry.getValue();

            history.putIfAbsent(testName, new ArrayList<>());
            history.get(testName).add(result);

            // Keep only last 10 runs
            if (history.get(testName).size() > 10) {
                history.get(testName).remove(0);
            }
        }
    }
}
