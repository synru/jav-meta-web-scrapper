from generic_update_detail import generic_update_detail
from datetime import datetime
import re
from operator import mul
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

class ave_update_detail(generic_update_detail):
        
    def after_soup_preparation(self, soup):
        self.container_element = soup.select_one("div.product-info-block-rev.mt-20")

    def get_element(self, soup, item):            
        element = self.container_element.find("span", text=item)
        if element == None:
            return None

        return element.next_sibling.next

    def get_actress_list(self, soup):
        element = self.get_element(soup, "主演女優")
        elements = element.find_all("a")
        return [element.text for element in elements]

    def get_genre_list(self, soup):
        element = self.get_element(soup, "カテゴリ")
        elements = element.find_all("a")
        return [element.text for element in elements]        

    def get_release_date(self, soup):
        element = self.get_element(soup, "発売日")
        date_str = element.next.strip()
        return datetime.strptime(date_str, '%m/%d/%Y')

    def get_length(self, soup):
        
        element = self.get_element(soup, "収録時間")
        lengthstr = element.text.strip()
        factors = (60, 1, 1/60)
        
        if lengthstr != "":
            sp = re.split(':|：|;', lengthstr)
            length = int(sum(map(mul, map(int, sp[:2]), factors)))
        else:
            length = None        
        
        return length


    def get_series(self, soup):
        element = self.get_element(soup, "シリーズ")
        if element == None:
            return None
        return element.select_one("a").text

    def get_resolution(self, soup):
        element = soup.select_one("div.additional-info")
        ls = [e.text for e in element.select("span.title")]

        filtered = list(filter(lambda t: "Kbps" in t or "kbps" in t, ls))

        try:
            s = sorted(filtered, key=lambda x: int(x.split("Kbps")[0].split("kbps")[0]), reverse=True)
            s = list(filter(lambda t: "X" in t or "x" in t, s[0].split(" ")))
            
            if len(s) == 0:
                return None

            res = s[0]
            return res
        except ValueError:
            filtered = list(filter(lambda t: "1920X1080" in t, filtered))
            if len(filtered) > 0:
                return "1920X1080"
