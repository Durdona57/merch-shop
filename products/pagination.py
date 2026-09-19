from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 9  # matches the 3-column product grid nicely
    page_size_query_param = "page_size"
    max_page_size = 50