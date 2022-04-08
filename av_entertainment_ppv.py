#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
from ave_load_movie_list import ave_load_movie_list
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from tqdm import tqdm
import requests

class ave(ave_load_movie_list):
    def __init__(self, studio, page):
        self.dbpath = 'db/movies.db'
        self.landing_page = page
        self.ending_page = None
        self.starting_page = 1

        self.studio = studio
        self.waiting_time = 0
        self.browser = None

class av_entertainment_ppv():

    def process_all(self):
        response = requests.get("https://www.aventertainments.com/ppv/ppv_studiolists.aspx?languageID=2&vodtypeid=1")
        html_doc = response.text
        soup = BeautifulSoup(html_doc, "html.parser")

        links = soup.find_all('a', {'href': re.compile(r'https://www.aventertainments.com/ppv/ppv_studioproducts.aspx\?StudioID=[0-9]+&languageID=2&VODTypeID=1')})
        lis = [(link.attrs['href'].split("StudioID=")[1].split("&")[0], link.text.split('(')[0].strip()) for link in links]

        lis = list(filter(lambda t: t[1] in ('帝 - ミカド -'), lis))

        for l in (pbar:= tqdm(lis)):
            studio = l[1]

            pbar.set_description("Processsing studio " + studio)

            v = ave(studio, "https://www.aventertainments.com/ppv/ppv_studioproducts.aspx?studioid="+ l[0] +"&languageID=1&vodtypeid=1&Rows=2&CountPage=%i")

            try:    
                v.process_all()
            finally:
                del v

        return

if __name__ == '__main__':
    uncensored  =  av_entertainment_ppv()
    uncensored.process_all()
