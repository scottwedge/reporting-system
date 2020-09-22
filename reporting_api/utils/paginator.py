import math

from eggit.paginator import Paginator


class PaginatorSon(Paginator):
    def __init__(self, page, per_page, pagination, items=None):
        self.page = page
        self.pages = math.ceil(pagination.total / per_page)
        self.per_page = per_page
        self.total = pagination.total
        if items is not None:
            self.items = items
        else:
            self.items = pagination.items

