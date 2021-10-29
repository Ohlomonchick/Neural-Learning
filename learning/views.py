import time

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.forms import inlineformset_factory, modelformset_factory
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView
from django import forms
from django.contrib import messages

from .forms import RegisterUserForm, LoginUserForm, TestForm, TestFormFormSet
from .models import *
from .utils import *

# from .serializers import QuestionSerializer, AnswerSerializer
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.generics import GenericAPIView
# from rest_framework.response import Response
# from .models import Question


class LearningHome(DataMixin, ListView):
    template_name = 'learning/index.html'
    context_object_name = 'posts'        # по умолчанию object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        historical = Articles.objects.filter(cat=Category.objects.get(slug='history'))
        c_def = self.get_user_context(title='Главная страница', cat_selected=0, historical=historical)
        return dict(list(context.items()) + list(c_def.items()))
        pass

    def get_queryset(self):
        pass


class TestsPage(DataMixin, ListView):
    model = Articles
    template_name = 'learning/tests_page.html'
    context_object_name = 'posts'        # по умолчанию object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=c.pk)
        context
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Articles.objects.filter(cat=Category.objects.get(slug=self.kwargs['cat_slug']))
        # return Articles.objects.select_related('cat')


class ShowArticle(DataMixin, DetailView):
    model = Articles
    template_name = 'learning/article.html'
    slug_url_kwarg = 'article_slug'        # по умолчанию просто slug, а для id - pk_url_kwarg
    context_object_name = 'article'

    def get_context_data(self, *, object_list=None, **kwargs):  # динамические данные(список, например)
        context = super().get_context_data(**kwargs)
        is_test = Question.objects.filter(article=context['article']).exists()
        if self.request.user.is_authenticated:
            is_finished = Answer.objects.filter(article=context['article'], user=self.request.user).exists()
        else:
            is_finished = False
        is_reccur = True if context['article'].slug == 'recurrent_networks' else False
        c_def = self.get_user_context(title=context['article'], is_test=is_test, is_finished=is_finished, is_reccur=is_reccur)
        return dict(list(context.items()) + list(c_def.items()))


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'learning/register.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация', cat_selected=6)
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):     # вызывается джангой при успешной регистрация
        user = form.save()
        login(self.request, user)
        return redirect('home')


def createAnswer(request, article_slug):

    article = Articles.objects.get(slug=article_slug)
    questions = Question.objects.filter(article=article).count()
    TestFormSet = modelformset_factory(model=Answer, fields=('choice',),  extra=questions)

    question_list = Question.objects.filter(article=article)
    user = request.user
    formset = TestFormSet(queryset=Articles.objects.none(), auto_id=False)
    for i in range(len(formset)):
        formset[i].fields['choice'] = forms.ModelChoiceField(queryset=Choice.objects.filter(question=question_list[i]))
        formset[i].fields['choice'].widget.attrs['required'] = True
        formset[i].fields['choice'].label = question_list[i].title
        formset[i].fields['choice'].empty_label = 'Ответ не выбран'
        formset[i].fields['id'].label = ''
        formset[i].fields['id'].widget.attrs['class'] = 'nothing'
    # form = TestForm()
    if request.method == 'POST':
        # form = TestForm(request.POST)
        formset = TestFormSet(request.POST)

        if formset.is_valid():
            total_exp = 0
            max_exp = Choice.objects.filter(article=article).aggregate(Sum('points'))['points__sum']
            ready_answers = Answer.objects.filter(article=article, user=user)
            if not ready_answers:
                for i in range(len(formset)):
                    form = formset[i].save(commit=False)
                    exp = form.choice.points
                    total_exp += exp
                    form.user = user
                    form.question = question_list[i]
                    form.article = article
                    # time.sleep(2)
                    form.save()
                user.profile.experience += total_exp
                lower_levels = Levels.objects.filter(points__lte=user.profile.experience)
                extra_message = ''
                level_points = user.profile.level.points
                if lower_levels:
                    levels = Levels.objects.filter(points__lte=user.profile.experience).count()
                    user.profile.level = Levels.objects.get(pk=lower_levels[levels - 1].pk + 1)
                    if user.profile.level.points > level_points:
                        extra_message = f'Вы достигли уровня{user.profile.level}!'
                user.profile.save()
                messages.success(request, f'Вы набрали {total_exp}/{max_exp} очков {extra_message} ')
            else:
                total_difference = 0
                for i in range(len(formset)):
                    form = formset[i].save(commit=False)
                    f_points = form.choice.points
                    a_points = ready_answers[i].choice.points
                    if ready_answers[i].choice != form.choice and f_points >= a_points:
                        difference = f_points - a_points
                        ready_answers[i].choice = form.choice
                        total_difference += difference
                        ready_answers[i].save()
                user.profile.experience += total_difference
                lower_levels = Levels.objects.filter(points__lte=user.profile.experience)
                extra_message = ''
                level_points = user.profile.level.points
                if lower_levels:
                    levels = Levels.objects.filter(points__lte=user.profile.experience).count()
                    user.profile.level = Levels.objects.get(pk=lower_levels[levels - 1].pk + 1)
                    if user.profile.level.points > level_points:
                        extra_message = f'Вы достигли уровня{user.profile.level}!'
                user.profile.save()

                messages.success(request, f'Вы увеличили свой результат на {total_difference} очков {extra_message} ')

            return redirect(article.cat.get_absolute_url())

    mixin = DataMixin()
    context = mixin.get_user_context()
    context['formset'] = formset
    context['user'] = user
    context['article'] = article
    context['title'] = 'Тест по теме ' + article.title

    return render(request, 'learning/test_form.html', context)


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'learning/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация', quests=Question.objects.all(), cat_selected=6)
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


# class ShowProfile(DataMixin):
#     template_name = 'learning/article.html'
#     # slug_url_kwarg = 'article_slug'        # по умолчанию просто slug, а для id - pk_url_kwarg
#     # context_object_name = ''
#
#     def get_context_data(self, request, *, object_list=None, **kwargs):  # динамические данные(список, например)
#         context = super().get_context_data(**kwargs)
#         c_def = self.get_user_context(title=context['article'])
#         return dict(list(context.items()) + list(c_def.items()))

def show_profile(request):

    mixin = DataMixin()
    context = mixin.get_user_context()
    # context['user'] = user
    context['cat_selected'] = 6
    context['title'] = 'Ваш профиль'

    return render(request, 'learning/profile.html', context)