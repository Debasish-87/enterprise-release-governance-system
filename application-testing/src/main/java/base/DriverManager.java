package base;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public class DriverManager {

    private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();

    public static void initDriver() {

        // अगर already driver initialized है तो return
        if (driver.get() != null) {
            return;
        }

        WebDriverManager.chromedriver().setup();

        ChromeOptions options = new ChromeOptions();

        // ============================
        // Common Chrome Arguments
        // ============================
        options.addArguments("--disable-notifications");
        options.addArguments("--disable-infobars");
        options.addArguments("--incognito");
        options.addArguments("--disable-popup-blocking");
        options.addArguments("--disable-extensions");
        options.addArguments("--remote-allow-origins=*");

        // Remove automation message
        options.setExperimentalOption("excludeSwitches", new String[]{"enable-automation"});
        options.setExperimentalOption("useAutomationExtension", false);

        // ============================
        // CI / Headless Detection
        // ============================
        boolean isCI = System.getenv("CI") != null;
        boolean isHeadless = System.getProperty("headless", "false").equalsIgnoreCase("true");

        // ============================
        // Headless / CI Mode
        // ============================
        if (isCI || isHeadless) {

            // Headless mode
            options.addArguments("--headless=new");

            // GitHub Actions Linux stability
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");
            options.addArguments("--disable-gpu");

            // Extra stability
            options.addArguments("--window-size=1920,1080");

        } else {
            // Local UI mode
            options.addArguments("--start-maximized");
        }

        // ============================
        // Create Driver
        // ============================
        driver.set(new ChromeDriver(options));
    }

    public static WebDriver getDriver() {
        return driver.get();
    }

    public static void quitDriver() {

        WebDriver currentDriver = driver.get();

        if (currentDriver != null) {
            try {
                currentDriver.quit();
            } catch (Exception ignored) {
            } finally {
                driver.remove();
            }
        }
    }
}
