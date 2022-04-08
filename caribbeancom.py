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

class generic_load_movie_list():

    def __init__(self):
        with open('config.yaml', encoding="utf-8") as f:
    
            data = yaml.load(f, Loader=yaml.FullLoader)["Caribbeancom"]
            self.dbpath = data["sqlite_db_path"]
            self.landing_page = data['landing_page']
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        options.add_argument("--log-level=3")
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def __del__(self):
        if self.browser != None:
            self.browser.quit()

    def get_total_pages(self, soup):
        pages = int(soup.select_one("div.pagination").select("a.pagination-item")[-2].select_one("div").text)
        return pages

    def process_all(self):
        url = self.landing_page % 1
        self.browser.get(url)

        #WebDriverWait(self.browser, 10).until_not(EC.presence_of_element_located((By.ID, "svg-loading")))
        html_doc = self.browser.page_source

        btitle = self.browser.title

        if btitle.startswith("404"):
            return None

        
        soup = BeautifulSoup(html_doc, 'html.parser')

        total_pages = self.get_total_pages(soup)
        page_items = []

        for i in (pbar:= tqdm(range(1, total_pages+1))):
            pbar.set_description("Processsing page %i" % i)
            if i > 1:
                url = self.landing_page % i
                self.browser.get(url)
                html_doc = self.browser.page_source

                btitle = self.browser.title

                if btitle.startswith("404"):
                    break

                soup = BeautifulSoup(html_doc, 'html.parser')

            divs = soup.select("div.entry")

            for div in divs:
                img = div.select_one("img.media-image")

                img_src = img.attrs["src"]

                link_a = div.select_one("a")
                link = link_a.attrs["href"]

                code = link.split("/")[2]

                title = div.select_one("div.meta-title").select_one("a").text.strip()
                
                
                page_items.append((code, title,img_src,link))


            self.save_basic_info(page_items)
            page_items = []
        return

    def save_basic_info(self,page_items):
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        try:
            cursor.executemany('INSERT INTO MovieCarib(code, title, thumbnail_src, detail_link) VALUES (?,?,?,?)', page_items)
            conn.commit()
        except BaseException as e:
            print(traceback.format_exc())
            conn.rollback()
        finally:            
            conn.close()
            return

