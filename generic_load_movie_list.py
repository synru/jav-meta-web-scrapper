#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import sqlite3
import traceback
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import yaml
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from sqlite3 import IntegrityError
import warnings
import requests

class generic_load_movie_list():

    def __init__(self, studio, waiting_time):
        with open('config.yaml', encoding="utf-8") as f:
    
            data = yaml.load(f, Loader=yaml.FullLoader)[studio]
            self.dbpath = data["sqlite_db_path"]
            self.landing_page = data['landing_page']
            self.starting_page = data.get('starting_page')
            if self.starting_page != None:
                self.starting_page = int(self.starting_page)
            else:
                self.starting_page = 1
            self.ending_page = data.get('ending_page')
            if self.ending_page != None:
                self.ending_page = int(self.ending_page)

        self.studio = studio
        self.waiting_time = waiting_time

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        options.add_argument("--log-level=3")
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def __del__(self):
        if self.browser != None:
            self.browser.quit()

    def get_total_pages(self, soup):
        pass

    def get_movie_element_list(self, soup):
        pass

    def get_code(self, element):
        pass
    def get_title(self, element):
        pass
    def get_img_src(self, element):
        pass
    def get_link(self, element):
        pass

    def get_soup(self, url):
        if self.browser != None:
            self.browser.get(url)

            html_doc = self.browser.page_source

            btitle = self.browser.title

            if btitle.startswith("404"):
                return None
        else:
            response = requests.get(url)
            html_doc = response.text

            if response.status_code == '404':
                return None

        return BeautifulSoup(html_doc, 'html.parser')

    def process_all(self):
        url = self.landing_page % 1

        soup = self.get_soup(url)

        if self.ending_page == None:
            total_pages = self.get_total_pages(soup)
        else:
            total_pages = self.ending_page

        page_items = []

        for i in (pbar:= tqdm(range(self.starting_page, total_pages+1))):
            pbar.set_description("Processsing page %i" % i)
            if i > 1:
                url = self.landing_page % i
                soup = self.get_soup(url)

            elements = self.get_movie_element_list(soup)

            for element in elements:
                code = self.get_code(element)
                title = self.get_title(element)
                img_src = self.get_img_src(element)
                link = self.get_link(element)                
                
                page_items.append((code, title,img_src,link, self.studio))


            self.save_basic_info(page_items)
            page_items = []
            if self.waiting_time != None and self.waiting_time >0:
                time.sleep(self.waiting_time)
        return

    def save_basic_info(self,page_items):
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        try:
            cursor.executemany('INSERT INTO MovieCarib(code, title, thumbnail_src, detail_link, studio) VALUES (?,?,?,?,?)', page_items)
            conn.commit()
        except IntegrityError as e:
            warnings.warn("Duplicate key in one the item : %s" % [c[0] for c in page_items])
            conn.rollback()            
        except BaseException as e:
            print(traceback.format_exc())
            conn.rollback()
        finally:            
            conn.close()
            return

