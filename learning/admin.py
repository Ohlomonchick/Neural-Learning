from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(Articles)
admin.site.register(Levels)


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'visible',
        'max_points',
        'article',
    )
    list_filter = ('article',)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'question',
        'points',
        'lock_other',
        'article',
    )
    list_filter = ('question',)


class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'question',
        'choice',
        'article',
    )
    list_filter = ('user',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Answer, AnswerAdmin)
