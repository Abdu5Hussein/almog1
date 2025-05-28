# pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size            = 20                # الافتراضي
    page_size_query_param = 'page_size'      # يسمح بتغييره من العميل
    max_page_size         = 100
