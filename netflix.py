'''Run netflix searches via Selenium'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import \
    staleness_of
from selenium.common.exceptions import StaleElementReferenceException,\
    NoSuchElementException, ElementNotVisibleException
from getpass import getpass
import time
import re
import sys
import operator
from collections import OrderedDict

LOGIN_URL = "https://signup.netflix.com/Login"

CATEGORY_ELEMENT_CLASSNAME = "lolomoRow"

class Netflix():
    def __init__(self, email, password, profilename=None, datadir=None):
        self.email = email
        self.password = password
        self.profilename = profilename
        self.datadir = datadir

        self.create_driver()  
        self.login()
        
        if profilename:
            self.select_profile()

    def __enter__(self):
        return self        
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.quit()        
        
    def login(self):
        '''Login to netflix'''
        try:
            self.driver.get(LOGIN_URL)
            self.driver.find_element_by_id('email').send_keys(self.email)
            entry = self.driver.find_element_by_id('password')
            entry.send_keys(self.password)
            entry.submit()    
            print "login complete"
        except NoSuchElementException as nse:
            # If already logged, Netflix redirects to the main page and this 
            # exception will occur and the URL will be different.  However if
            # the URL is the same then something failed.
            if self.driver.current_url == LOGIN_URL:
                print "login failed"
                raise nse
        
    def create_driver(self):
        opts = webdriver.chrome.options.Options()
        opts.add_argument("--maximize")
        opts.add_argument("--kiosk")
        opts.add_argument("--new-window")
        opts.add_argument("--disable-new-tab-first-run")
        if self.datadir:
            opts.add_argument("--user-data-dir=%s" % self.datadir)
        driver = webdriver.Chrome(chrome_options=opts)        
        driver.implicitly_wait(3)
        self.driver = driver        
        
    def get_driver(self):
        return self.driver
    
    def click_through_to_main_page(self, element):    
        element.click()
        WebDriverWait(self.driver, 10, 1, (ElementNotVisibleException, StaleElementReferenceException)).until(lambda x: x.find_element_by_class_name(CATEGORY_ELEMENT_CLASSNAME).is_displayed())
    
    def select_profile(self):        
        profiles = self.driver.find_elements_by_class_name('profile-link')
        for result in profiles:
            if result.text.find(self.profilename) != -1:
                print result.text
                self.click_through_to_main_page(result)
                break      
            
    def get_profiles(self):
        '''
        TODO need to exclude the add profile link
        '''
        profiles = []
        profileNameSpans = self.driver.find_elements_by_class_name('profile-name')
        for name in profileNameSpans:
            profiles.append(name.text)
        return profiles   
    
    def get_category_titles(self, category_element):
        # get video_id  and aria_label (title)
        titles_dict = {}
        titleCardDivConts = category_element.find_elements_by_class_name("title-card-container")
        for titleCardDivCont in titleCardDivConts:
            titleCardDivs = titleCardDivCont.find_elements_by_xpath("div")
            for card in titleCardDivs:
                title = card.get_attribute("aria-label")
                data_reactid = card.get_attribute("data-reactid")
                video_id = re.match(r".*title_([0-9]*)_.*", data_reactid).group(1)
                titles_dict[title] = 'http://www.netflix.com/watch/' + video_id
        
        return OrderedDict(sorted(titles_dict.items(), key=lambda x: x[0]))    
    
    def get_categories(self, specific_category=None):
        try:
            categories_dict = {}
            category_count = 0
            categories = []
            
            categories = self.driver.find_elements_by_class_name(CATEGORY_ELEMENT_CLASSNAME)
            while True:
                time.sleep(3)
                cnt = len(categories)
                categories = self.driver.find_elements_by_class_name(CATEGORY_ELEMENT_CLASSNAME)
                if (cnt == len(categories)):
                    break
            for result in categories: 
                if specific_category:
                    if specific_category == result.text:
                        return self.get_category_titles(result)
                    else:
                        continue
                categories_dict[result.text] = self.get_category_titles(result)       
            categories_dict = OrderedDict(sorted(categories_dict.items(), key=lambda x: x[0]))
            return categories_dict    
        except StaleElementReferenceException:
            print "caught stale exception"
            return self.get_categories()    
        
    def click_continue_playing(self):
        '''
        Click the continue playing button on the playback interrupter pop-up.
        
        button class="button continue-playing" type="button"><span><span class="nf-icons icon-player-play"></span>Continue Playing</span></button>
        '''
        continueButtons = self.driver.find_elements_by_css_selector("button[class='button continue-playing']")
        for button in continueButtons:
            if button.text.find("Continue Playing") != -1:
                button.click()
                return

