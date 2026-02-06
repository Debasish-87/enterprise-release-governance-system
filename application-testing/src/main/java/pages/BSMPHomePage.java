package pages;

import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;

public class BSMPHomePage {

    private WebDriver driver;
    private WebDriverWait wait;

    public BSMPHomePage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(12));
    }

    // ===============================
    // Page Locators
    // ===============================
    private By heading = By.xpath("//h1[contains(text(),'Big Mart Sales Prediction')]");

    private By itemWeight = By.name("item_weight");
    private By itemFatContent = By.name("item_fat_content");
    private By itemVisibility = By.name("item_visibility");
    private By itemType = By.name("item_type");
    private By itemMrp = By.name("item_mrp");
    private By outletYear = By.name("outlet_establishment_year");
    private By outletSize = By.name("outlet_size");
    private By outletLocationType = By.name("outlet_location_type");
    private By outletType = By.name("outlet_type");
    private By extraFeature1 = By.name("extra_feature_1");
    private By extraFeature2 = By.name("extra_feature_2");

    private By predictButton = By.xpath("//button[contains(text(),'Predict Sales')]");

    // Prediction result
    private By predictionBox = By.xpath("//div[contains(@class,'prediction-box')]");
    private By predictionText = By.xpath("//div[contains(@class,'prediction-box')]//p");

    // ===============================
    // Wait Helpers
    // ===============================
    private WebElement waitForVisible(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
    }

    private WebElement waitForClickable(By locator) {
        return wait.until(ExpectedConditions.elementToBeClickable(locator));
    }

    private void waitForPageStable() {
        try {
            Thread.sleep(300); // small stability buffer (super helpful in UI apps)
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    // ===============================
    // Safe Retry Helper (Stale Fix)
    // ===============================
    private void retry(Runnable action) {
        int attempts = 0;
        while (attempts < 2) {
            try {
                action.run();
                return;
            } catch (StaleElementReferenceException e) {
                attempts++;
                waitForPageStable();
            }
        }
        // last attempt (throw actual error)
        action.run();
    }

    // ===============================
    // Safe Dropdown Select (Value Check)
    // ===============================
    private void safeSelectByValue(By locator, String value) {

        retry(() -> {
            WebElement el = waitForVisible(locator);
            Select select = new Select(el);

            boolean found = select.getOptions()
                    .stream()
                    .anyMatch(o -> value.equals(o.getAttribute("value")));

            if (!found) {
                throw new RuntimeException("❌ Invalid dropdown value: '" + value + "' for locator: " + locator);
            }

            select.selectByValue(value);
        });
    }

    // ===============================
    // Page Actions
    // ===============================

    public boolean isHeadingVisible() {
        try {
            return waitForVisible(heading).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public void enterItemWeight(String value) {
        retry(() -> {
            WebElement el = waitForVisible(itemWeight);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void selectItemFatContent(String value) {
        safeSelectByValue(itemFatContent, value);
    }

    public void enterItemVisibility(String value) {
        retry(() -> {
            WebElement el = waitForVisible(itemVisibility);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void selectItemType(String value) {
        safeSelectByValue(itemType, value);
    }

    public void enterItemMRP(String value) {
        retry(() -> {
            WebElement el = waitForVisible(itemMrp);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void enterOutletYear(String value) {
        retry(() -> {
            WebElement el = waitForVisible(outletYear);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void selectOutletSize(String value) {
        safeSelectByValue(outletSize, value);
    }

    public void selectOutletLocationType(String value) {
        safeSelectByValue(outletLocationType, value);
    }

    public void selectOutletType(String value) {
        safeSelectByValue(outletType, value);
    }

    public void enterExtraFeature1(String value) {
        retry(() -> {
            WebElement el = waitForVisible(extraFeature1);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void enterExtraFeature2(String value) {
        retry(() -> {
            WebElement el = waitForVisible(extraFeature2);
            el.clear();
            el.sendKeys(value);
        });
    }

    public void clickPredict() {
        retry(() -> waitForClickable(predictButton).click());

        //  Predict click ke baad prediction box ka wait
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(predictionBox));
        } catch (Exception ignored) {
        }
    }

    public boolean isPredictionBoxVisible() {
        try {
            return waitForVisible(predictionBox).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public String getPredictionText() {
        try {
            return waitForVisible(predictionText).getText();
        } catch (Exception e) {
            return "";
        }
    }

    // ==========================================================
    //  Dynamic Form Fill (for DataProvider / Multiple Cases)
    // ==========================================================
    public void fillPredictionForm(
            String itemWeightValue,
            String fatContentValue,
            String visibilityValue,
            String itemTypeValue,
            String mrpValue,
            String yearValue,
            String outletSizeValue,
            String locationTypeValue,
            String outletTypeValue,
            String extra1Value,
            String extra2Value
    ) {

        enterItemWeight(itemWeightValue);
        selectItemFatContent(fatContentValue);
        enterItemVisibility(visibilityValue);
        selectItemType(itemTypeValue);
        enterItemMRP(mrpValue);
        enterOutletYear(yearValue);
        selectOutletSize(outletSizeValue);
        selectOutletLocationType(locationTypeValue);
        selectOutletType(outletTypeValue);
        enterExtraFeature1(extra1Value);
        enterExtraFeature2(extra2Value);
    }

    // ==========================================================
    //  Old One-shot fill (optional, backward compatible)
    // ==========================================================
    public void fillPredictionForm() {
        fillPredictionForm(
                "15.5",
                "1",
                "0.10",
                "6",
                "200",
                "2005",
                "1",
                "0",
                "1",
                "10",
                "20"
        );
    }
}
