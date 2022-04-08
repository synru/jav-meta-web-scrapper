from generic_update_detail import generic_update_detail
from datetime import datetime
import re
from operator import mul
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import warnings

class tenmusume_update_detail(generic_update_detail):
    def __init__(self):
        generic_update_detail.__init__(self, "天然むすめ",1)
        
    def after_loading_page(self):
        #element = self.browser.find_element(by=By.CSS_SELECTOR, value="#page > div.container-main > div.wrapper > main > div.contents > div.movie-info.section.divider > button > label")
        #element.click()
        pass

    def after_soup_preparation(self, soup):
        self.container_element = soup.select_one("div.movie-info.section")

    def get_element(self, soup, item):            
        element = self.container_element.find("span", text=item)
        if element == None:
            return None

        return element.next_sibling

    def get_actress_list(self, soup):
        element = self.get_element(soup, "出演")
        elements = element.find_all("a")
        return [element.text for element in elements]

    def get_genre_list(self, soup):
        element = self.get_element(soup, "タグ")
        if element != None:
            elements = element.find_all("a")
            return [element.text for element in elements]

    def get_release_date(self, soup):
        element = self.get_element(soup, "配信日")

        if element != None:
            date_str = element.text.strip().replace('"', "").split(" – ")[0]
                
            try:
                return datetime.strptime(date_str, '%Y/%m/%d')
            except ValueError as e:
                warnings.warn("Unable to interpret date %s" % date_str)
                return None

    def get_length(self, soup):
        element = self.get_element(soup, "再生時間")
        
        lengthstr = None
        try:
            lengthstr = element.text

            factors = (60, 1, 1/60)
            
            if lengthstr != "":
                sp = re.split(':|：|;', lengthstr)
                length = int(sum(map(mul, map(int, sp[:2]), factors)))
            else:
                length = None        
            
            return length
        except ValueError as e:
            
            warnings.warn("Unexpected length value : %s" % lengthstr)

    def get_series(self, soup):
        element = self.get_element(soup, "シリーズ:")
        if element == None:
            return None
        series = element.next.next.text.strip()

        if series == "-----":
            series = None
        return series

    def get_resolution(self, soup):
        title = soup.select_one("#movies > div.container > div.inner-container > div.movie-info.section > div.heading > h1").text

        cursor = self.conn.cursor()
        try:
            cursor.execute("select resolution from MovieHeyd where title = ? and studio = ?", (title, self.studio))
            row = cursor.fetchone()
            if row != None:
                return row[0]
            return None
        finally:
            cursor.close()
        




if __name__ == '__main__':
    studio  =  tenmusume_update_detail()
    try:
        studio.process_all()
    finally:
        del studio
