from django.core.paginator import Paginator

from yatube.settings import QTY_POSTS


def get_page(request, post):
    paginator = Paginator(post, QTY_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
