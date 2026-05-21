import pyautogui
import time
'''
#Mouse Operations
#pyautogui.moveTo(100,100)
#time.sleep(2)
#pyautogui.rightClick(100,100)

#time.sleep(4)

#pyautogui.click(886,824)

#pyautogui.doubleClick(100,100)

#pyautogui.drag(100,100,200,200)

'''
#Keyboard Operations
#time.sleep(3)
#pyautogui.click(858,987)

#time.sleep(3)
#   pyautogui.write("SocialEagle.ai")

#typewrite("SocialEagle.ai")

#pyautogui.press('enter')

#pyautogui.hotkey('ctrl','a')

#Image

try:
    location = pyautogui.locateOnScreen('D:\GenAI_Social_Eagle/images.png', confidence=0.8)
    print(location)
    time.sleep(2)
    pyautogui.click(pyautogui.center(location))
except pyautogui.ImageNotFoundException:
    print("Image not found on screen.")