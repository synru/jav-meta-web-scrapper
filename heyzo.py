from generic_load_movie_list import generic_load_movie_list

class heyzo_load_movie_list(generic_load_movie_list):

    def __init__(self):
        generic_load_movie_list.__init__(self, "Heyzo",0)

    def get_total_pages(self, soup):
        pages = int(soup.select_one("span.list_pagetotal").text)
        return pages

    def get_movie_element_list(self, soup):
        container = soup.select_one("#movies")
        #skip element without data-movie-id attribute
        divs = container.find_all("div", {"data-movie-id":True})
        return divs

    def get_code(self, element):
        code = element.attrs["data-movie-id"]
        return code

    def get_title(self, element):
        title = element.select_one("img.lazy").attrs["title"]
        return title

    def get_img_src(self, element):
        img_src = element.select_one("img.lazy").attrs["data-original"]
        return img_src

    def get_link(self, element):
        link = element.select_one("a").attrs["href"]
        return link



if __name__ == '__main__':
    studio  =  heyzo_load_movie_list()
    try:
        studio.process_all()
    finally:
        del studio
