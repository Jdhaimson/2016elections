# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Results(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://www.cnn.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.output_file = './scraped_data.txt'

    def wait_and_scroll(self, is_first=False):
        driver = self.driver
        if is_first:
            driver.execute_script("window.scrollBy(0,1500)")
        else:
            driver.execute_script("window.scrollBy(0,document.body.scrollHeight - 2100)")
        wait_time = 2
        time.sleep(wait_time)

    
    def test_results(self):
        primaries = [
            ("Kansas", "KS", "Republican", 1, "/election/primaries/counties/ks/Rep"),
            ("Kansas", "KS", "Democrat", 1, "/election/primaries/counties/ks/Dem"),
            ("Kentucky", "KY", "Republican", 6, "/election/primaries/counties/ky/Rep"),
            ("Louisiana", "LA", "Republican", 4, "/election/primaries/counties/la/Rep"),
            ("Louisiana", "LA", "Democrat", 4, "/election/primaries/counties/la/Dem"),
            ("Nebraska", "NE", "Democrat", 5, "/election/primaries/counties/ne/Dem")
            '''
            ("Hawaii", "HI", "Republican", 1, "/election/primaries/counties/hi/Rep"),
            ("Idaho", "ID", "Republican", 3, "/election/primaries/counties/id/Rep"),
            ("Michigan", "MI", "Republican", 5, "/election/primaries/counties/mi/Rep")
            '''
        ]

        for primary in primaries:
            self.scrape_primary_data(primary)

    def scrape_primary_data(self, (state, state_abbreviation, party, num_pages, path)):
        driver = self.driver
        driver.get(self.base_url + path)
        self.wait_and_scroll()
        self.page = 1

        html = []
        for i in xrange(num_pages):
            html.append(driver.find_element_by_class_name("pagination").get_attribute('innerHTML'))
            if self.page < num_pages:
                self.go_to_next_page()
        html_str = ''.join(html)

        with open(self.output_file, 'a') as f:
            f.write('("' + state + '", "' + state_abbreviation + '", "' + party + '", """' + html_str + '""")\n')
            

    def go_to_next_page(self):
        driver = self.driver
        self.page += 1
        if (self.page % 10 == 0):
            driver.find_element_by_css_selector("div.pagination__button.pagination__button--next").click()
        else:
            i = (self.page % 10) # + 1
            layer = (self.page / 10) + 1
            layer_text = ('[' + str(layer) + ']')  if (layer > 1) else ''
            xpath = "//div[@id='mount']/main/div/div[2]/div/div/div/nav/div" + layer_text + "/div[" + str(i) + "]"
            driver.find_element_by_xpath(xpath).click()

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
