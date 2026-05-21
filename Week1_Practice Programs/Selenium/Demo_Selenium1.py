from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import tempfile
import os

# =====================================================
# CREATE TEMP CHROME PROFILE
# =====================================================

temp_profile = tempfile.mkdtemp()

# =====================================================
# CHROME OPTIONS
# =====================================================

options = webdriver.ChromeOptions()

# Use temporary profile
options.add_argument(f"--user-data-dir={temp_profile}")

# Disable automation info
options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation"]
)

options.add_experimental_option(
    "useAutomationExtension",
    False
)

# Disable password manager completely
prefs = {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_settings.popups": 0
}

options.add_experimental_option("prefs", prefs)

# Disable popup features
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-save-password-bubble")
options.add_argument("--disable-features=PasswordLeakDetection")
options.add_argument("--disable-features=AutofillServerCommunication")
options.add_argument("--disable-infobars")

# Optional
options.add_argument("--start-maximized")

# =====================================================
# START DRIVER
# =====================================================

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 10)

base_url = "https://the-internet.herokuapp.com"

# =====================================================
# TEST 1 — LOGIN TEST
# =====================================================

print("\n===== TEST 1 : LOGIN TEST =====")

driver.get(base_url + "/login")

username = wait.until(
    EC.visibility_of_element_located((By.ID, "username"))
)

password = wait.until(
    EC.visibility_of_element_located((By.ID, "password"))
)

username.send_keys("tomsmith")
password.send_keys("SuperSecretPassword!")

login_button = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[type='submit']")
    )
)

login_button.click()

message = wait.until(
    EC.visibility_of_element_located((By.ID, "flash"))
).text

if "You logged into a secure area!" in message:
    print("LOGIN TEST PASSED")
else:
    print("LOGIN TEST FAILED")

# =====================================================
# TEST 2 — CHECKBOX TEST
# =====================================================

print("\n===== TEST 2 : CHECKBOX TEST =====")

driver.get(base_url + "/checkboxes")

checkboxes = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "input[type='checkbox']")
    )
)

checkboxes[0].click()

if checkboxes[0].is_selected():
    print("CHECKBOX TEST PASSED")
else:
    print("CHECKBOX TEST FAILED")

# =====================================================
# TEST 3 — DROPDOWN TEST
# =====================================================

print("\n===== TEST 3 : DROPDOWN TEST =====")

driver.get(base_url + "/dropdown")

dropdown_element = wait.until(
    EC.visibility_of_element_located((By.ID, "dropdown"))
)

dropdown = Select(dropdown_element)

dropdown.select_by_visible_text("Option 2")

selected = dropdown.first_selected_option.text

if selected == "Option 2":
    print("DROPDOWN TEST PASSED")
else:
    print("DROPDOWN TEST FAILED")

# =====================================================
# TEST 4 — ALERT TEST
# =====================================================

print("\n===== TEST 4 : ALERT TEST =====")

driver.get(base_url + "/javascript_alerts")

alert_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[text()='Click for JS Alert']")
    )
)

alert_button.click()

alert = wait.until(EC.alert_is_present())

print("Alert Text:", alert.text)

alert.accept()

result = wait.until(
    EC.visibility_of_element_located((By.ID, "result"))
).text

if "successfully clicked" in result:
    print("ALERT TEST PASSED")
else:
    print("ALERT TEST FAILED")

# =====================================================
# TEST 5 — FILE UPLOAD TEST
# =====================================================

print("\n===== TEST 5 : FILE UPLOAD TEST =====")

driver.get(base_url + "/upload")

sample_file = "sample_upload.txt"

with open(sample_file, "w") as f:
    f.write("Selenium File Upload Test")

absolute_path = os.path.abspath(sample_file)

upload_input = wait.until(
    EC.presence_of_element_located((By.ID, "file-upload"))
)

upload_input.send_keys(absolute_path)

upload_button = wait.until(
    EC.element_to_be_clickable((By.ID, "file-submit"))
)

upload_button.click()

uploaded_text = wait.until(
    EC.visibility_of_element_located((By.TAG_NAME, "h3"))
).text

if "File Uploaded!" in uploaded_text:
    print("FILE UPLOAD TEST PASSED")
else:
    print("FILE UPLOAD TEST FAILED")

# =====================================================
# FINISH
# =====================================================

print("\n===== ALL TESTS COMPLETED SUCCESSFULLY =====")

input("\nPress Enter to close browser...")

driver.quit()