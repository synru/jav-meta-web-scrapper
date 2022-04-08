#!/usr/bin/python
# -*- coding: UTF-8 -*-
from nntplib import NNTPDataError
from bs4 import BeautifulSoup
import sqlite3
import traceback
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import yaml
from datetime import datetime
from operator import mul
import re
from urllib.parse import urljoin
import time

class generic_update_detail():
    def __init__(self, studio, waiting_time):
        with open('config.yaml', encoding="utf-8") as f:
    
            data = yaml.load(f, Loader=yaml.FullLoader)[studio]
            self.dbpath = data["sqlite_db_path"]
            self.landing_page = data['landing_page']
                
        self.studio = studio
        self.waiting_time = waiting_time
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        options.add_argument("--log-level=3")
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.conn = sqlite3.connect(self.dbpath)

    def __del__(self):
        print("In destructor")
        if self.browser != None:
            self.browser.quit()
        if self.conn != None:
            self.conn.close()

    def process_all(self):

        cursor = self.conn.cursor()
        cursor.execute("select code, detail_link from MovieCarib where release_date is null and studio = ? order by code", (self.studio,))
        rows = cursor.fetchall()

        for row in (pbar := tqdm(rows)):
            code = row[0]
            detail_link = row[1]
            pbar.set_description("Processing %s" % code)
            genres, actresses, length, release_date, resolution, series = self.extract_html(detail_link)

            if release_date == None:
                continue
            self.sql_update(self.conn, code, genres, actresses, length, release_date, resolution, series)
        
            if self.waiting_time != None and self.waiting_time >0:
                time.sleep(self.waiting_time)


    def get_actress_list(self, soup):
        pass

    def get_genre_list(self, soup):
        pass

    def get_release_date(self, soup):
        pass

    def get_length(self, soup):
        pass

    def get_series(self, soup):
        pass

    def get_resolution(self, soup):
        pass

    def after_loading_page(self):
        pass

    def after_soup_preparation(self, soup):
        pass

    def extract_html(self, detail_link):
        url = urljoin(self.landing_page, detail_link)
        

        self.browser.get(url)
        self.after_loading_page()

        html_doc = self.browser.page_source
        #response = requests.get(url)
        #status = response.status_code
        #html_doc = response.text

        
        btitle = self.browser.title

        if btitle.startswith("404"):
            return None, None, None, None
        #elif html_doc == "":
        #    return None, None, None, None
        #elif status != 200:
        #    sys.exit(status)
        soup = BeautifulSoup(html_doc, 'html.parser')
        self.after_soup_preparation(soup)

        try:
            genres = self.get_genre_list(soup)

            #actress
            
            actresses = self.get_actress_list(soup)

            # Length
            length = self.get_length(soup)

            release_date = self.get_release_date(soup)

            resolution = self.get_resolution(soup)

            series = self.get_series(soup)

            return genres, actresses, length, release_date, resolution, series
        except (AttributeError, ValueError) as exec:
            raise RuntimeError("Unable to process link : %s" % url) from exec
    def sql_update(self,conn, code, genres, actresses, length, release_date, resolution, series):
        
        try:
            
            cursor = conn.cursor()
            genre_str = None
            actress_str = None

            if genres != None:
                ob = list(zip([code]*len(genres), genres, [code]*len(self.studio)))
                cursor.executemany("insert into MovieCaribGenre (movie_code, genre, studio) values (?, ?, ?)", ob)
                genre_str = ";".join(genres)
            if actresses != None:
                ob = list(zip([code]*len(actresses), actresses, [code]*len(self.studio)))
                cursor.executemany("insert into MovieCaribActress (movie_code, actress, studio) values (?, ?, ?)", ob)
                actress_str = ";".join(actresses)

            cursor.execute("UPDATE  moviecarib set length=?, release_date =?, genre=?, actress=?, resolution=?, series=? where code=?;", (length, release_date, genre_str, actress_str, resolution, series, code))
            conn.commit()
            
        except BaseException as e:
            conn.rollback()
            print(traceback.format_exc())
        pass        


