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

class main():

    def __init__(self):
        with open('config.yaml', encoding="utf-8") as f:
    
            data = yaml.load(f, Loader=yaml.FullLoader)["Caribbeancom"]
            self.dbpath = data["sqlite_db_path"]
            self.landing_page = data['series_landing_page']
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        options.add_argument("--log-level=3")
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.conn = sqlite3.connect(self.dbpath)

    def __del__(self):
        if self.browser != None:
            self.browser.quit()
        if self.conn != None:
            self.conn.close()

    def process_all(self):
        url = self.landing_page
        self.browser.get(url)

        #WebDriverWait(self.browser, 10).until_not(EC.presence_of_element_located((By.ID, "svg-loading")))
        html_doc = self.browser.page_source

        soup = BeautifulSoup(html_doc, 'html.parser')

        element = soup.select_one("#cat-series")

        elements = element.select("a.list-button")

        for series_element in (pbar:= tqdm(elements)):
            series = series_element.text.strip()
            url = series_element.attrs["href"]
            pbar.set_description("Processsing page %s" % series)

            self.browser.get("https://www.caribbeancom.com" + url)
            html_doc = self.browser.page_source

            soup = BeautifulSoup(html_doc, 'html.parser')
            element = soup.select_one("div.section")

            movies = element.findAll("a", {"itemprop" : "url"})

            for movie in (pbar_movie:= tqdm(movies)):
                movie_link = movie.attrs["href"]
                t = movie.text
                pbar_movie.set_description("Processsing link %s - title %s" % (movie_link, t))
                code = movie_link.split("/")[2]
                self.save(code, series)
        return

    def save(self,code, series):
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('update MovieCarib set series =? where code=?', (series, code))
            self.conn.commit()
        except BaseException as e:
            print(traceback.format_exc())
            self.conn.rollback()
            return

if __name__ == '__main__':
    uncensored  =  main()
    try:
        uncensored.process_all()
    finally:
        del uncensored
