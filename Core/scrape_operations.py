import types

import pandas as pd

from selenium.webdriver.common.keys import Keys

class ScrapeOp():

    scraper = None
    xpath = None
    target = None

    is_multiple = False
    is_safe = True

    def __init__(self, is_multiple=False, is_safe=True):
        self.is_multiple = is_multiple
        self.is_safe = is_safe
    
    def __call__(self, **kwds):
        if self.xpath != None:
            if not self._evaluate_xpath():
                print(f'opsss, {self.xpath}')
                return None
        return self.execute()
    
    def _evaluate_xpath(self):
        if type(self.xpath) is str:
            return True
        elif type(self.xpath) is list: # select first existing
            return self._evaluate_xpath_list()       
        elif type(self.xpath) is set: # select first existing but optional
            return self._evaluate_xpath_set()
        
    def _evaluate_xpath_list(self):
        timeout = 2 if type(self.xpath[0]) is str else self.xpath[0]
        for xp in self.xpath:
            try:
                _ = self.scraper.safe_find_element(xp, timeout=timeout)
                self.xpath = xp
                return True
            except:
                pass
        if not (type(self.xpath) is str):
            raise Exception(f'Failed xpath_list evaluation on: {self.xpath}')
        return False

    def _evaluate_xpath_set(self):
        self.xpath = list(self.xpath)
        timeout = 2 if type(self.xpath[0]) is str else self.xpath[0]
        for xp in self.xpath:
            try:
                _ = self.scraper.safe_find_element(xp, timeout=timeout)
                self.xpath = xp
                return True
            except:
                pass
        return False
    
    def execute(self):
        if self.is_safe:
            self.target = self.scraper.safe_find_elements(self.xpath) if self.is_multiple else self.scraper.safe_find_element(self.xpath)
        else:
            try:
                self.target = self.scraper.find_elements(self.xpath) if self.is_multiple else self.scraper.find_element(self.xpath)
            except:
                self.target = None

class ClickOp(ScrapeOp):

    def __init__(self, is_safe=True):
        super().__init__(is_safe=is_safe)

    def execute(self):
        super().execute()
        if self.is_safe or (self.target != None and not self.is_safe):
            self.scraper.driver.execute_script("arguments[0].click();", self.target)
        return

class ReadOp(ScrapeOp):
    
    attribute = None

    def __init__(self, attribute=None, is_multiple=False):
        super().__init__(is_multiple)
        self.attribute = attribute

    def execute(self):      
        super().execute()
        if self.is_multiple:
            output = [el.get_attribute(self.attribute) if self.attribute != None else el.text for el in self.target]
        else:
            output = self.target.get_attribute(self.attribute) if self.attribute != None else self.target.text
        return output
    
class WriteOp(ScrapeOp):
    
    content = None
    enter = False

    def __init__(self, content, enter=False):
        super().__init__()
        self.content = content
        self.enter = enter

    def execute(self):
        super().execute()
        self.content = self.content() if isinstance(self.content, types.FunctionType) else self.content
        self.target.send_keys(self.content)
        if self.enter:
            self.target.send_keys(Keys.ENTER)
        return
    
class ScrollOp(ScrapeOp):

    def __init__(self):
        super().__init__()

    def execute(self):
        self.scraper.scroll_window()
        return
    
class KeyOp(ScrapeOp):


    key = Keys.ENTER
    
    def __init__(self, key=None):
        super().__init__()
        self.key = key if key != None else Keys.ENTER

    def execute(self):
        self.target = self.scraper.driver.switch_to.active_element
        if self.target == None:
            self.xpath = self.xpath if self.target!=None else '/html/body'
            super().execute()
        self.target.send_keys(self.key)
        return
    
class OutputOperations():
    
    make_df = lambda data, kwargs={}: pd.DataFrame(**{'data':data, **kwargs})
    write_df = lambda df, fn, kwargs={}: df.to_csv(**{'path_or_buf': fn, **kwargs}, index=False) if 'index' in kwargs else  df.to_csv(**{'path_or_buf': fn, **kwargs})
    make_write_df = lambda make_kwargs, write_kwargs: OutputOperations.write_df(OutputOperations.make_df(make_kwargs), write_kwargs)