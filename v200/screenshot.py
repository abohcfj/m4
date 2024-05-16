from PIL import ImageGrab,Image
import pyautogui

import time
def pil_grab_pil():
    im = ImageGrab.grab()
    im.save("obj.png")

def gui_grab_pill():
    pyautogui.screenshot("obj.png") 

while True:
    gui_grab_pill()