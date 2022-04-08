from generic_load_movie_list import generic_load_movie_list

class ave_load_movie_list(generic_load_movie_list):

    def get_total_pages(self, soup):
        alist = soup.select_one("ul.pagination").select("a")
        if len(alist) > 1:
            pages = int(alist[-2].text)
        else:
            pages = 1
        return pages

    def get_movie_element_list(self, soup):
        container = soup.select_one("div.row.shop-product-wrap.grid.mb-10")
        divs = container.select("div.single-slider-product.grid-view-product")

        #divs = list(filter(lambda t: "Vol.1 " in self.get_title(t) or "Vol.3 " in self.get_title(t) or "Vol.4 " in self.get_title(t) or "Vol.5 " in self.get_title(t) or "Vol.7 " in self.get_title(t) or "Vol.8 " in self.get_title(t) or "Vol.9 " in self.get_title(t) or "Vol.13 " in self.get_title(t) or "Vol.14 " in self.get_title(t), divs))

        return divs

    def get_code(self, element):
        e = self.get_img_src(element)
        code = e.split("/")[-1].split(".")[0].split("_")[0]
        return code

    def get_title(self, element):
        title = element.select("a")[1].text
        return title

    def get_img_src(self, element):
        img_src = element.select_one("img").attrs["src"]
        return img_src

    def get_link(self, element):
        link = element.select_one("a").attrs["href"]
        return link
