class Paginator(object):
    def __init__(self, page, pages, per_page, items, total):
        self.page = page
        self.pages = pages
        self.per_page = per_page
        self.items = items
        self.total = total

    def get_dict(self):
        return dict(
            page=self.page,
            pages=self.pages,
            per_page=self.per_page,
            items=self.items,
            total=self.total
        )
