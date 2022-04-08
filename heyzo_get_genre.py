#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
import json
import sqlite3
import requests
import sys, os
import traceback
from tqdm import tqdm
from sys import exit

jcensored_dict ={
'sqlite3db_path':'C:/Users/sunlu/Works/AV/javhoo_actresses/db/javhooDB.db'
}
class JavHoo_Uncensored():
    censored_total = 0
    process_num_at_a_time = 1
    def __init__(self,jdict):
        self.dbpath = jdict['sqlite3db_path']
    def process_all(self):
        sql_creat = '''
        select Code from Movies where Genre ="" and type in ('Uncensored') and instr(code, "heyzo-")=1 and TEMP is null order by id;
        '''
        conn = sqlite3.connect(self.dbpath)
        try:
            
            cursor = conn.cursor()
            cursor.execute(sql_creat)
            rows = cursor.fetchall()

            for row in (pbar := tqdm(rows)):
                code = row[0]
                pbar.set_description("Processing %s" % code)
                genres = self.extract_html(code)
                self.sql_update(conn, code, genres)
            conn.close()
        except BaseException as e:
            #exc_type, exc_obj, exc_tb = sys.exc_info()
            #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            conn.rollback()
            #print("Exception : ", e, fname, exc_tb.tb_lineno, exc_tb.format_exc())
            print(traceback.format_exc())
        pass
    def extract_html(self, code):
        n = code.split("-")[1];
        url = 'https://www.heyzo.com/moviepages/' + n +'/index.html'
        response = requests.get(url)
        status = response.status_code
        html_doc = response.text

        if status == 404: 
            return
        elif html_doc == "":
            return
        elif status != 200:
            sys.exit(status)
        soup = BeautifulSoup(html_doc, 'html.parser')
        
        div = soup.find("tr",class_="table-tag-keyword-small")
        if div == None:
            return

        div = div.next_sibling.next_sibling
        links = div.find_all("a")
        genres = [l.text.strip() for l in links]
        return genres

    def sql_update(self,conn, code, genres):
        
        try:
            
            cursor = conn.cursor()
            if genres != None:
                ob = list(zip([code]*len(genres), genres))
                cursor.executemany("insert into MovieGenre (MovieCode, Genre) values (?, ?)", ob)
                genre_str = ";".join(genres)
                cursor.execute("UPDATE            movies set Genre=?, TEMP=1                where Code=?;", (genre_str, code))            
            else:
                cursor.execute("UPDATE            movies set TEMP=1                where Code=?;", [code])            
            conn.commit()
            
        except BaseException as e:
            conn.rollback()
            print(traceback.format_exc())
        pass
if __name__ == '__main__':
    # print("Reading ",jcensored_dict['html_path'],"...")
     censored  =  JavHoo_Uncensored(jcensored_dict)
     censored.process_all()
     print("see ",jcensored_dict['sqlite3db_path'])
