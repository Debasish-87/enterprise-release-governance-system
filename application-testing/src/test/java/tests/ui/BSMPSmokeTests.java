package tests.ui;

import base.BaseTest;
import base.DriverManager;
import io.qameta.allure.*;
import org.openqa.selenium.WebDriver;
import org.testng.Assert;
import org.testng.ITestResult;
import org.testng.annotations.*;

import pages.BSMPHomePage;

@Epic("BSMP - Big Mart Sales Prediction")
@Feature("UI Tests")
public class BSMPSmokeTests extends BaseTest {

    @Test(groups = {"Smoke"})
    @Story("Home page should load successfully")
    @Severity(SeverityLevel.CRITICAL)
    public void verifyHomePageLoads() {

        WebDriver driver = DriverManager.getDriver();
        BSMPHomePage homePage = new BSMPHomePage(driver);

        Assert.assertTrue(homePage.isHeadingVisible(),
                "❌ Home page heading not visible!");
    }

    /**
     *  Multiple cases run using DataProvider
     * Every row = one test execution
     */
    @Test(dataProvider = "salesData", groups = {"Regression", "Critical"})
    @Story("User should get sales prediction after submitting form")
    @Severity(SeverityLevel.BLOCKER)
    @Description("Runs multiple prediction cases with different inputs and validates output")
    public void verifyPredictionGenerated_MultipleCases(
            String caseName,
            String itemWeight,
            String fatContent,
            String visibility,
            String itemType,
            String mrp,
            String year,
            String outletSize,
            String locationType,
            String outletType,
            String extra1,
            String extra2
    ) {

        WebDriver driver = DriverManager.getDriver();
        BSMPHomePage homePage = new BSMPHomePage(driver);

        //  Allure me case name clear show hoga
        Allure.step("Running Test Case: " + caseName);

        Assert.assertTrue(homePage.isHeadingVisible(),
                "❌ Home page not loaded properly!");

        //  Allure Step
        Allure.step("Filling prediction form with values");

        //  Attachments (strong reporting)
        Allure.addAttachment("Case Name", caseName);
        Allure.addAttachment("item_weight", itemWeight);
        Allure.addAttachment("item_fat_content", fatContent);
        Allure.addAttachment("item_visibility", visibility);
        Allure.addAttachment("item_type", itemType);
        Allure.addAttachment("item_mrp", mrp);
        Allure.addAttachment("outlet_establishment_year", year);
        Allure.addAttachment("outlet_size", outletSize);
        Allure.addAttachment("outlet_location_type", locationType);
        Allure.addAttachment("outlet_type", outletType);
        Allure.addAttachment("extra_feature_1", extra1);
        Allure.addAttachment("extra_feature_2", extra2);

        // Fill form with dynamic values
        homePage.fillPredictionForm(
                itemWeight,
                fatContent,
                visibility,
                itemType,
                mrp,
                year,
                outletSize,
                locationType,
                outletType,
                extra1,
                extra2
        );

        Allure.step("Clicking Predict button");
        homePage.clickPredict();

        Allure.step("Validating prediction output");
        Assert.assertTrue(homePage.isPredictionBoxVisible(),
                "❌ Prediction box not visible!");

        String resultText = homePage.getPredictionText();

        Assert.assertTrue(resultText.toLowerCase().contains("predicted"),
                "❌ Prediction text not correct: " + resultText);

        Allure.addAttachment("Prediction Result Text", resultText);
    }

    /**
     *  After every test case (DataProvider included)
     * Refresh page so next case starts clean
     */
    @AfterMethod(alwaysRun = true)
    public void resetPageAfterEachCase(ITestResult result) {

        WebDriver driver = DriverManager.getDriver();

        if (driver != null) {

            //  Allure Step (extra clean reporting)
            Allure.step("Resetting UI for next test case (refresh)");

            driver.navigate().refresh();
        }
    }

    /**
     *  DataProvider = 10 strong test cases
     *
     * NOTE:
     * Tumhare dropdown me outlet_location_type ke valid values
     * mostly 0 and 1 hi lag rahe hai.
     *
     * Isliye maine 2 hata diya.
     */
    @DataProvider(name = "salesData")
    public Object[][] salesData() {
        return new Object[][]{

                {"Case 1 - Standard Input", "15.5","1","0.10","0","200","2005","1","0","1","10","20"},
                {"Case 2 - Medium Weight", "10.2","2","0.05","6","150","2010","2","1","0","5","12"},
                {"Case 3 - High Visibility", "25.0","0","0.20","14","320","1999","0","0","2","8","15"},
                {"Case 4 - Low MRP", "8.0","1","0.12","3","110","2008","2","1","1","6","9"},
                {"Case 5 - Balanced Input", "18.7","2","0.08","10","250","2001","1","1","2","12","18"},
                {"Case 6 - Modern Year", "12.4","0","0.15","5","175","2015","0","1","0","4","7"},
                {"Case 7 - Old Outlet", "22.9","1","0.03","8","305","1995","2","0","2","15","25"},
                {"Case 8 - Very Low Weight", "5.5","2","0.18","12","95","2018","1","1","1","3","5"},
                {"Case 9 - Extreme MRP", "30.0","0","0.25","2","400","1987","0","1","2","20","30"},
                {"Case 10 - Normal Flow", "16.2","1","0.07","9","210","2003","2","0","0","9","14"}
        };
    }
}
