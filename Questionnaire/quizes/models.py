from django.db import models
from django.core.validators import MaxLengthValidator


class Quiz(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=400)

# TODO may need order
class Page(models.Model):
    quiz = models.ForeignKey(Quiz)

# TODO may need order
class Question(models.Model):
    page = models.ForeignKey(Page)
    text = models.TextField(validators=[MaxLengthValidator(4000)])
    # TODO enum ?
    type = models.CharField(max_length=20)

class Choice(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=200)
    value = models.IntegerField(default=0)

class Result(models.Model):
    quiz = models.ForeignKey(Quiz)
    score = models.IntegerField(default=0)

