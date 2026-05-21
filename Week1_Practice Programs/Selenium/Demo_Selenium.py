from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://the-internet.herokuapp.com/?utm_source=chatgpt.com")
#driver.back()
#driver.forward()
#driver.refresh()

#finding elements
#element = driver.find_element(By.ID,"content")
element = driver.find_element(By.XPATH,'//*[@id="content"]/ul/li[1]')

#wait

wait = WebDriverWait(driver,10)
element = wait.until(EC.presence_of_element_located((By.ID,"content")))

#Interactions

element.click()
element.send_keys('Social Eagle')
element.clear()

#Screenshots
driver.save_screenshot('Demo.png')
