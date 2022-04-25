# dependency for Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Dependency for wait element
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException,
                                        TimeoutException,
                                        StaleElementReferenceException,
                                        ElementNotInteractableException,
                                        SessionNotCreatedException)

from utils import *
import base64
from io import BytesIO
import cv2
import glob
import os
import numpy as np
import time
from cairosvg import svg2png
from PIL import Image
from detect_image import *

class Boursorama():

    def __init__(self):
        print("here")
        self.navigateur = None
        self.debug = True
        self.navigateur = self.broswer()
        self.ut = Utils(self.navigateur)
        self.login("111111", "1234")

    def broswer(self):
        print(bcolors.OKGREEN + "connect to boursorama" + bcolors.ENDC)

        url = "https://clients.boursorama.com/connexion/"
        options_firefox = Options()
        if self.debug == True:
            options_firefox.headless = False
        else:
            options_firefox.headless = True

        self.navigateur = webdriver.Firefox()

        self.navigateur.maximize_window()
        time.sleep(2)
        self.navigateur.get(url)
        return self.navigateur

    def login(self, ID, PASSWORD):
        time.sleep(2)
        #click close popup
        self.ut.retry(method=By.XPATH,
                      element="//button[@id='didomi-notice-agree-button']",
                      objects="click_element", timeout=5, retry=0)
        time.sleep(1)

        inputs = self.ut.retry(method=By.XPATH, element="//input[@id='form_clientNumber']",
                                   objects="input", send_keys=ID, method_input=By.ID,
                                   element_input="submit", message="Enter ID with input",
                                   message_fail="Timeout check element recheck...",
                                   timeout=1, check_login=False, timeout_fail=2, retry=0)

        # click next
        self.ut.retry(method=By.XPATH,
                      element="//button[@id='']",
                      objects="click_element", timeout=5, retry=0)
        time.sleep(1)
        self.pad_resolve(PASSWORD)

        # self.ut.retry(method=By.XPATH,
        #               element="//button[@id='']",
        #               objects="click_element", timeout=5, retry=0)

    def pad_resolve(self, PASSWORD):
        # DETECT PAD
        # get all_image pad
        img_pad_button = self.ut.retry(method=By.XPATH,
                             element="//button[@class='sasmap__key']",
                             objects="all_elements", timeout=0.01, retry=3)
        img_pad = self.ut.retry(method=By.XPATH,
                             element="//img[@class='sasmap__img']",
                             objects="all_elements", timeout=0.01, retry=3)

        #download pad_images
        number_images = 0
        for i, img in enumerate(img_pad):
            with open("images/{}.png".format(i), "wb") as fh:
                fh.write(base64.b64decode(img.get_attribute('src').split('data:image/svg+xml;base64,')[1]))
                fh.close()

                image_stream = BytesIO()
                image_stream.write(base64.b64decode(img.get_attribute('src').split('data:image/svg+xml;base64,')[1]))
                image_stream.seek(0)

                png = svg2png(bytestring=image_stream.read())
                pil_img = Image.open(BytesIO(png)).convert('RGBA')
                pil_img.save('images/{}.png'.format(i))
                number_images = i

        # crop_images
        imdir = 'images/'
        ext = ['png', 'jpg', 'gif']    # Add image formats here
        files = []
        [files.extend(glob.glob(imdir + '*.' + e)) for e in ext]
        absolute_path = os.path.join(os.getcwd(), 'images','0.png');
        images = [cv2.imread("{}".format(file)) for file in files]

        for img in glob.glob("images/*.png"):
            cv_img = cv2.imread(img)
            y=0
            x=0
            h=30
            w=30
            crop = cv_img[y:y+h, x:x+w]
            cv2.imwrite("{}".format(img), crop)

        listes = [(x, y) for x in range(0, 10) for y in range(0, 10)]
        print(bcolors.OKBLUE + "Analysing Pad ... please wait" + bcolors.ENDC)

        dict_number = {}
        for a, i in listes:
            check_image = calcule_image(i, a)
            if check_image == True:
                dict_number["{}".format(i)] = a

        for key, value in dict_number.items():
            print("debug - image: {} is {}".format(key, value))

        for password in PASSWORD:
            for i, pad in enumerate(img_pad_button):
                if dict_number[str(i)] == int(password):
                    print("debug - click to position: {} for number {}".format(i, password))
                    pad.click()

        time.sleep(5)


if __name__ == "__main__":
    Boursorama()
