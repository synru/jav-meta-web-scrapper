#!/usr/bin/python
# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
import json
import sqlite3
import requests

juncensored_dict ={
   # 'html_path':'C:/Users/sunlu/Works/AV/javhoo_actresses/db/j.html',
'html_path':'C:/Users/sunlu/Works/AV/javhoo_actresses/a.html',
'sqlite3db_path':'C:/Users/sunlu/Works/AV/javhoo_actresses/db/javhooDB.db'
}
class av_entertainment():
    uncensored_total = 0
    process_num_at_a_time = 1
    def __init__(self,jdict):
        self.htmlpath = jdict['html_path']
        self.dbpath = jdict['sqlite3db_path']
        self.uncensored_total = 0
        self.process_num_at_a_time = 30
    def get_soup(self):
        avhtml = open(self.htmlpath,'r',encoding='utf-8')
        avsoup = BeautifulSoup(avhtml.read(),'lxml')
        return avsoup
    def process_all(self):
        avsoup = self.get_soup()
        wdivs = avsoup.find_all('a', {'href': re.compile(r'https://www.aventertainments.com/studio_products.aspx\?StudioID=[0-9]+&Dept_ID=29&languageID=2')})
        self.uncensored_total = len(wdivs)
        self.quick_save_to_sqlite3(wdivs)
        # for w in wdivs:
        #     article = w.article
        #     self.process(article)
        return
    def quick_save_to_sqlite3(self,wdivs):
        i = 0
        av_index = 0
        reach_total = False
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()
        while i < int(self.uncensored_total/self.process_num_at_a_time)+1:
            sql_insert = '''
            INSERT INTO
                uncensored(id,
                    ufanhao,utitle,uimgurl,udate)
            VALUES (null,?,?,?,?);
            '''
            data = []
            j = 0
            while j < min(self.process_num_at_a_time,self.uncensored_total):
                w = wdivs[av_index]
                info_dict = self.get_infodict(w)
                data.append(tuple(info_dict.values()))
                av_index += 1
                j = j+1
                if(av_index>=self.uncensored_total):
                    reach_total = True
                    break
            i = i+1
    # https://stackoverflow.com/questions/15513854/       sqlite3-warning-you-can-only-execute-one-statement-at-a-time
            sql_insert = sql_insert[:-1]
            try:
                #cursor.executemany(sql_insert,data)
                # conn.commit()
                print(av_index)
            except BaseException as e:
                conn.rollback()
                print(data)
                print('except...', e)
            if(reach_total):
                conn.commit()
                conn.close()
                print("End.")
                return
        pass
    def process(self,article):
        info_dict = self.get_infodict(article)
        print(info_dict)
        # print(article)
        return
    def get_infodict(self,article):
        id = self.get_id(article)
        infodict = {
            'studio_id': id,
            'studio_name': self.get_name(article),
            'studio_en_name': self.get_en_name(id)
        }
        print(infodict)
        return infodict

    def get_id(self,article):
        href =  article.attrs['href']
        id = re.search("StudioID=([^&]+)", href).group(1)
        return id

    def get_name(self,article):
        name = article.text
        name = re.sub(" (\([0-9]+\))", "", name,1)
        return name

    def get_en_name(self,id):
        response = requests.get("https://www.aventertainments.com/studio_products.aspx?StudioID=" + id + "&Dept_ID=29&languageID=1")
        html_doc = response.text

        avsoup = BeautifulSoup(html_doc, 'html.parser')
        div = avsoup.find("div",class_="section-title")
        h2 = div.h2
        t = h2.text
        name = re.sub(" (\([0-9]+ Matches\))", "", t,1)
        return name

    def create_table(self):
        sql_creat = '''
        create table uncensored(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ufanhao text,utitle text,
        uimgurl text,
        udate text
        );
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            cursor.execute(sql_creat)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def drop_table(self):
        sql_drop = '''
        drop table if exists uncensored;
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            cursor.execute(sql_drop)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def slow_save_to_sqlite3(self,dict_data):
        sql_insert = '''
        INSERT INTO
            uncensored(id,
                ufanhao,utitle,uimgurl,udate)
        VALUES (null,?,?,?,?);
        '''
        try:
            conn = sqlite3.connect(self.dbpath)
            cursor = conn.cursor()
            self.insert(cursor,sql_insert,dict_data)
            conn.commit()
            conn.close()
        except BaseException as e:
            conn.rollback()
            print('except...', e)
        pass
    def insert(self,cursor,sql_insert,dict_data):
        cursor.execute(sql_insert,tuple(dict_data.values()))
        pass    
if __name__ == '__main__':
    print("Reading ",juncensored_dict['html_path'],"...")
    uncensored  =  av_entertainment(juncensored_dict)
    #uncensored.drop_table()
    #uncensored.create_table()
    uncensored.process_all()
    print("see ",juncensored_dict['sqlite3db_path'])
