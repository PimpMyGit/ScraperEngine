import time

from typing import Any

import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import action_keys as _AK
from .scrape_actions import Action, Procedure, Iterated

from typing import Any

class Scraper():

    name = None
    driver = None
    procedure = None
    
    def __init__(self, name, procedure, chromedriver_path='chromedriver.exe'):
        self.name = name
        self.procedure = procedure
        self.driver = webdriver.Chrome(chromedriver_path)
        self.driver.maximize_window()

    def build(self):
        self._inject_driver(self.procedure)

    def _inject_driver(self, procedure):
        if isinstance(procedure, Iterated):
            self._inject_driver(procedure.action)
        elif isinstance(procedure, Procedure):
            for subprocedure in procedure.actions.values():
                self._inject_driver(subprocedure)
        else:
            procedure.scraper = self

    def run_procedure(self):
        self.procedure.run()

    def open_page(self, url):
        if url != self.driver.current_url:
            self.driver.get(url)

    def find_element(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)

    def safe_find_element(self, xpath, timeout=30):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return self.find_element(xpath)
    
    def find_elements(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)
    
    def safe_find_elements(self, xpath, timeout=30):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return self.find_elements(xpath)
    
    def scroll_window(self):
        self.driver.execute_script('window.scrollBy(0, window.innerHeight)')