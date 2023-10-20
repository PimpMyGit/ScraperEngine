import time

from typing import Any

import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

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
    
    def find_sub_element(self, parent, child_xpath):
        if type(parent) is str:
            parent = self.find_element(parent)
            child_xpath = child_xpath if child_xpath.startswith('//') else parent + child_xpath[1:]
        out = parent.find_element_by_xpath(child_xpath)
        return out
    
    def safe_find_sub_element(self, parent_xpath, child_xpath, timeout=30):
        absolute_path = child_xpath if not child_xpath.startswith('//') else parent_xpath + child_xpath[1:]
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, absolute_path)))
        return self.find_sub_element(parent_xpath, absolute_path)
    
    def find_sub_elements(self, parent, child_xpath):
        if type(parent) is str:
            parent = self.find_elements(parent)
            child_xpath = child_xpath if child_xpath.startswith('//') else parent + child_xpath[1:]
        return parent.find_element_by_xpaths(child_xpath)
    
    def safe_find_sub_elements(self, parent_xpath, child_xpath, timeout=30):
        absolute_path = child_xpath if not child_xpath.startswith('//') else parent_xpath + child_xpath[1:]
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, absolute_path)))
        return self.find_sub_elements(parent_xpath, absolute_path)

    def scroll_window(self):
        self.driver.execute_script('window.scrollBy(0, window.innerHeight)')

    def scroll_element(self, element):
        self.driver.execute_script('arguments[0].scrollBy(0, arguments[0].scrollHeight)', element)