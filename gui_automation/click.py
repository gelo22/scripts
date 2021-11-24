#!/usr/bin/env python

import sys
import time
import pyautogui
import datetime

# py -m pip install pyautogui

while True:
    print(datetime.datetime.now())
    time.sleep(30)
    pyautogui.click(100, 100, button='secondary')
    time.sleep(5)
    pyautogui.click(500, 500, button='secondary')

