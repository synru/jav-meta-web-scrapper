from ave_load_movie_list import ave_load_movie_list
from ave_update_detail import ave_update_detail

class catcheye_load_movie_list(ave_load_movie_list):

    def __init__(self):
        ave_load_movie_list.__init__(self, "CATCHEYE",0)

class catcheye_update_detail(ave_update_detail):

    def __init__(self):
        ave_update_detail.__init__(self, "CATCHEYE",0)

if __name__ == '__main__':
    studio  =  catcheye_update_detail()
    try:
        studio.process_all()
    finally:
        del studio
