import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up download directory
DOWNLOAD_DIR = "/Users/manavkanaganapalli/Desktop/Airport Landings Database and Webapp/old"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Set up Chrome driver options
options = webdriver.ChromeOptions()
options.headless = False  # Set to True once stable
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
})

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

URL = "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr"

for year in range(2018, 2026):
    for month in range(1, 13):
        try:
            driver.get(URL)

            # Select year
            wait.until(EC.presence_of_element_located((By.ID, "cboYear")))
            Select(driver.find_element(By.ID, "cboYear")).select_by_visible_text(str(year))

            # Select month
            month_name = time.strftime("%B", time.strptime(str(month), "%m"))
            Select(driver.find_element(By.ID, "cboPeriod")).select_by_visible_text(month_name)

            # Uncheck pre-zipped if needed
            try:
                prezip = driver.find_element(By.ID, "chkDownloadZip")
                if prezip.is_selected():
                    prezip.click()
            except:
                pass

            # Check all checkboxes
            checkboxes = driver.find_elements(By.XPATH, '//input[@type="checkbox" and contains(@id,"chk_")]')
            for cb in checkboxes:
                try:
                    if not cb.is_selected():
                        cb.click()
                except Exception as e:
                    print(f"⚠️ Failed to check box: {e}")

            # Click the download button
            download_btn = wait.until(EC.element_to_be_clickable((By.ID, "btnDownload")))
            download_btn.click()

            print(f"✅ Triggered download for {year}-{month:02d}")
            time.sleep(10)  # Wait for download to complete

        except Exception as e:
            print(f"❌ Error for {year}-{month:02d}: {e}")

driver.quit()
