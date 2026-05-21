import pyautogui
import time
import webbrowser

# Give yourself time
print("Starting in 5 seconds...")
time.sleep(5)

# Open Google directly
webbrowser.open("https://www.google.com")

# Wait until browser fully opens
time.sleep(8)

# Focus address/search bar
pyautogui.hotkey('ctrl', 'l')

time.sleep(1)

# Type search text slowly
pyautogui.write('South Africa score', interval=0.15)

time.sleep(1)

# Press Enter
pyautogui.press('enter')

print("Search completed")