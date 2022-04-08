from generic_load_movie_list import generic_load_movie_list

class onepondo_load_movie_list(generic_load_movie_list):

    def __init__(self):
        generic_load_movie_list.__init__(self, "一本道",10)

    def get_total_pages(self, soup):
        pages = int(soup.select_one("ul.pagination").select("a")[-2].text)
        return pages

    def get_movie_element_list(self, soup):
        divs = soup.select("div.grid-item")
        return divs

    def get_code(self, element):
        l = self.get_link(element)
        code = l.split("/")[2]
        return code

    def get_title(self, element):
        title = element.select_one("div.meta-title").text.strip()
        return title

    def get_img_src(self, element):
        img_src = element.select_one("img.media-thum-image").attrs["src"]
        return img_src

    def get_link(self, element):
        link = element.select_one("a.entry-meta").attrs["href"]
        return link



if __name__ == '__main__':
    studio  =  onepondo_load_movie_list()
    try:
        studio.process_all()
    finally:
        del studio
