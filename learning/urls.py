from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from neural import settings
from .views import *

if settings.DEBUG:
    cache_time = 0
else:
    cache_time = 60

urlpatterns = [
    path('', cache_page(cache_time)(LearningHome.as_view()), name='home'),
    # path('about/', about, name='about'),
    path('article/<slug:article_slug>/test/', createAnswer, name='answer'),
    # path('contact/', contact, name='contact'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', show_profile, name='profile'),
    # path('question/', GetQuestion.as_view(), name='question'),
    # path('question/answer', QuestionAnswer.as_view(), name='answer'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('article/<slug:article_slug>/', ShowArticle.as_view(), name='article'),
    path('category/<slug:cat_slug>/', TestsPage.as_view(), name='category'),
]
