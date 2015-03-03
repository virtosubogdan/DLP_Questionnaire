from django.db import models
from django.core.validators import MaxLengthValidator


class Quiz(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=400)

    def __str__(self):
        return "Question "+self.name;

    def get_first_page(self):
        return self.page_set.order_by('sequence_number')[:1][0]

# TODO may need order
class Page(models.Model):
    quiz = models.ForeignKey(Quiz)
    sequence_number = models.IntegerField(default=1, unique=True)

    def __str__(self):
        return "Quiz "+self.quiz.name+", Page "+ str(self.id) +", nr "+str(self.sequence_number)

    def next(self):
        next_list = Page.objects.filter(quiz=self.quiz).order_by('sequence_number').filter(
            sequence_number__gt=self.sequence_number)[:1]
        if not next_list:
            return None
        return next_list[0]
    def previous(self):
        prev_list = Page.objects.filter(quiz=self.quiz).order_by('-sequence_number').filter(
            sequence_number__lt=self.sequence_number)[:1]
        if not prev_list:
            return None
        return prev_list[0]

# TODO may need order
class Question(models.Model):
    page = models.ForeignKey(Page)
    text = models.TextField(validators=[MaxLengthValidator(4000)])
    # TODO enum ?
    type = models.CharField(max_length=20)

    def __str__(self):
        return "Question "+ str(self.id)

class Choice(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=200)
    value = models.IntegerField(default=0)

    def __str__(self):
        return "Choice "+self.text

class Result(models.Model):
    quiz = models.ForeignKey(Quiz)
    score = models.IntegerField(default=0)

    def __str__(self):
        return "Result "+str(self.id)+" Score:"+ str(self.score)

