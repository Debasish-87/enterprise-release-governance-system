package base;

import io.qameta.allure.Allure;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.ITestResult;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import utils.ConfigReader;

import java.io.ByteArrayInputStream;

public class BaseTest {

    @BeforeMethod(alwaysRun = true)
    public void setup() {

        DriverManager.initDriver();

        WebDriver driver = DriverManager.getDriver();

        String url = ConfigReader.getProperty("url");
        driver.get(url);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown(ITestResult result) {

        WebDriver driver = DriverManager.getDriver();

        // Screenshot only on failure
        if (driver != null && result.getStatus() == ITestResult.FAILURE) {

            byte[] screenshot = ((TakesScreenshot) driver)
                    .getScreenshotAs(OutputType.BYTES);

            Allure.addAttachment(
                    "❌ Failed Screenshot",
                    new ByteArrayInputStream(screenshot)
            );
        }

        DriverManager.quitDriver();
    }
}
