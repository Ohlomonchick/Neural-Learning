from django import template
from learning.models import *

register = template.Library()


@register.simple_tag
def show_is_test(post):
    is_test = Question.objects.filter(article=post).exists()

    return is_test
