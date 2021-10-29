from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    photo = models.ImageField(upload_to="photos", verbose_name="Фото", null=True)
    level = models.ForeignKey('Levels', on_delete=models.PROTECT, verbose_name="Уровень доступа", null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['id']


class Articles(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name="Контент")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Превью")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Категория")
    level = models.ForeignKey('Levels', on_delete=models.PROTECT, verbose_name="Уровень доступа")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', kwargs={'article_slug': self.slug})

    class Meta:
        verbose_name = "Статьи"
        verbose_name_plural = "Статьи"
        ordering = ['id']


class Levels(models.Model):
    points = models.IntegerField(verbose_name="Необходимые очки")

    def __str__(self):
        return str(self.id)

    # def get_absolute_url(self):
    #     return reverse('category', kwargs={'level_id': self.pk})

    class Meta:
        verbose_name = "Уровни"
        verbose_name_plural = "Уровни"
        ordering = ['id']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.ForeignKey('Levels', on_delete=models.PROTECT,
                              verbose_name="Уровень доступа", default=1)
    experience = models.IntegerField(verbose_name="Опыт", default=0)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Question(models.Model):
    title = models.CharField(max_length=4096)
    visible = models.BooleanField(default=False)
    max_points = models.FloatField()

    article = models.ForeignKey('Articles', on_delete=models.PROTECT, verbose_name="Статья")

    def __str__(self):
           return self.title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=4096)
    points = models.FloatField()
    lock_other = models.BooleanField(default=False)

    article = models.ForeignKey('Articles', on_delete=models.PROTECT, verbose_name="Статья")

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    choice = models.ForeignKey(Choice, on_delete=models.DO_NOTHING)
    created = models.DateTimeField(auto_now_add=True)

    article = models.ForeignKey('Articles', on_delete=models.PROTECT, verbose_name="Статья")

    def __str__(self):
        return self.choice.title

    def get_absolute_url(self):
        return reverse('test', kwargs={'article_slug': self.question.article.slug})