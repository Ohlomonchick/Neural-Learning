from django.db.models import Count
from django.core.cache import cache
from neural.settings import DEBUG

from .models import *

menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Добавить статью', 'url_name': 'add_page'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
]

cache_time = 0 if DEBUG else 60


class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        cats = cache.get('cats')
        if not cats:
            # cats = Category.objects.annotate(Count('women'))
            cats = Category.objects.all()
            cache.set('cats', cats, cache_time)

        user_menu = menu.copy()
        # if not self.request.user.is_authenticated:
        #     user_menu.pop(1)

        context['menu'] = user_menu
        context['cats'] = cats
        context['reccur'] = Articles.objects.get(slug='recurrent_networks')
        if 'cat_selected' not in context:
            context['cat_selected'] = 0

        return context