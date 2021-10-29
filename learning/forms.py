from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from .models import *


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    # level = forms.ModelChoiceField('Levels', default=Levels.objects.all()[0], verbose_name="Уровень доступа", null=True)

    # experience = models.IntegerField(default=0)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class TestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.article = kwargs.pop('article', None)
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)
        self.fields['choice'].required = True

        # self.initial['user'] = self.user
        # self.fields['user'].initial = self.user
        # self.fields['user'].widget.attrs['disabled'] = True
        # self.fields['article'].empty_label = self.article
        # self.fields['article'].widget.attrs['disabled'] = True
        # self.fields['question'].empty_label = self.question
        # self.fields['question'].widget.attrs['disabled'] = True

    class Meta:
        model = Answer
        fields = ['choice']
        # exclude = ('user',)
        widgets = {
            # 'user': forms.HiddenInput(),
            # 'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
        }

    def clean_user(self):
        # user = self.cleaned_data['user']
        # if not user:
        #     user = self.request.user
        #     raise ValidationError('Длина превышает 100 символов')

        return self.instance.user


TestFormFormSet = modelformset_factory(Answer, fields=['choice'], extra=8)