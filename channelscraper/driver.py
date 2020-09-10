import os
import platform
from config import Config
from selenium.webdriver import Chrome, Remote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import chromedriver_autoinstaller


class Driver:
    driver = None
    config = Config.getConfig()

    @staticmethod
    def getDriver():
        """ Static access method. """
        if Driver.driver is None:
            Driver()
        return Driver.driver
    
    @staticmethod
    def closeDriver():
        Driver.driver.quit()

    def __init__(self):
        """ Virtually private constructor. """
        if Driver.driver is not None:
            raise Exception("This class is a singleton!")
        else:
            if Driver.config.get("driver_mode") == "live":
                Driver.driver = Remote("http://127.0.0.1:4444/wd/hub", DesiredCapabilities.CHROME)
            else:
                chromedriver_autoinstaller.install() 
                Driver.driver = webdriver.Chrome()
