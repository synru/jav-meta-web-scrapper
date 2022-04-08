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

class main():
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
        print("In destructor")
        if self.browser != None:
            self.browser.quit()

    def process_all(self):

        conn = sqlite3.connect(self.dbpath)
        try:
            
            cursor = conn.cursor()
            cursor.execute("select code, release_date, detail_link from MovieCarib where release_date is null order by code")
            rows = cursor.fetchall()

            for row in (pbar := tqdm(rows)):
                code = row[0]
                release_date = row[1]
                detail_link = row[2]
                pbar.set_description("Processing %s" % code)
                genres, actresses, length, release_date = self.extract_html(detail_link)

                if release_date == None:
                    continue
                self.sql_update(conn, code, genres, actresses, length, release_date)
            
        except BaseException as e:
            print(traceback.format_exc())
            conn.rollback()
        finally:
            conn.close()
        pass
    def extract_html(self, detail_link):
        url = 'https://www.caribbeancom.com' + detail_link
        self.browser.get(url)
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
        
        try:
            elements = soup.select("a.spec-item");
            genres = [l.text.strip() for l in elements]

            #actress
            elements = soup.select_one("span.spec-content").select("span")
            actresses = [x.text for x in elements]

            # Length
            lengthstr = soup.find("span", text="再生時間").next_sibling.next.next.next.text.strip().replace(" ","")
            #t1 = datetime.strptime(lengthstr, "%H:%M:%S")
            #t2 = datetime(1900,1,1)

            #length = int((t1-t2).total_seconds() / 60.0)

            factors = (60, 1, 1/60)

            
            if lengthstr != "":
                sp = re.split(':|：|;', lengthstr)
                length = int(sum(map(mul, map(int, sp[:2]), factors)))
            else:
                length = None

            datestr = soup.find("span", text="配信日").next.next.next.text

            release_date = datetime.strptime(datestr, '%Y/%m/%d')


            #title = soup.select_one("#title-bg").next.next.text.strip()


            return genres, actresses, length, release_date
        except (AttributeError, ValueError) as exec:
            raise RuntimeError("Unable to process link : %s" % url) from exec
    def sql_update(self,conn, code, genres, actresses, length, release_date):
        
        try:
            
            cursor = conn.cursor()
            genre_str = None
            actress_str = None

            if genres != None:
                ob = list(zip([code]*len(genres), genres))
                cursor.executemany("insert into MovieCaribGenre (movie_code, genre) values (?, ?)", ob)
                genre_str = ";".join(genres)
            if actresses != None:
                ob = list(zip([code]*len(actresses), actresses))
                cursor.executemany("insert into MovieCaribActress (movie_code, actress) values (?, ?)", ob)
                actress_str = ";".join(actresses)

            cursor.execute("UPDATE  moviecarib set length=?, release_date =?, genre=?, actress=?  where code=?;", (length, release_date, genre_str, actress_str, code))            
            conn.commit()
            
        except BaseException as e:
            conn.rollback()
            print(traceback.format_exc())
        pass        


if __name__ == '__main__':

    uncensored  =  main()
    try:
        uncensored.process_all()
    finally:
        del uncensored
