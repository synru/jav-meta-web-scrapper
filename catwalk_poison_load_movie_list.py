from generic_load_movie_list import generic_load_movie_list

class catwalk_poison_load_movie_list(generic_load_movie_list):

    def __init__(self):
        generic_load_movie_list.__init__(self, "キャットウォーク",0)

    def get_total_pages(self, soup):
        pages = int(soup.select_one("ul.pagination").select("a")[-2].text)
        return pages

    def get_movie_element_list(self, soup):
        container = soup.select_one("div.row.shop-product-wrap.grid.mb-10")
        divs = container.select("div.single-slider-product.grid-view-product")
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



if __name__ == '__main__':
    studio  =  catwalk_poison_load_movie_list()
    try:
        studio.process_all()
    finally:
        del studio
