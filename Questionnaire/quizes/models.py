from django.db import models
from django.core.validators import MaxLengthValidator


class Quiz(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=400)

    def __str__(self):
        return "Question " + self.name

    def get_first_page(self):
        return self.page_set.order_by('sequence_number')[:1][0]

    def average_score(self):
        total = 0
        attempts = 0
        for result in self.result_set.all():
            total += result.score
            attempts += 1
        if not attempts:
            return None
        else:
            return total/attempts


# TODO may need order
class Page(models.Model):
    quiz = models.ForeignKey(Quiz)
    sequence_number = models.IntegerField(default=1)

    class Meta:
        unique_together = ('quiz', 'sequence_number')

    def __str__(self):
        return "Quiz " + self.quiz.name + ", Page " + str(self.id) + ", nr " + str(self.sequence_number)

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

    def make_answers(self, session):
        answers = Answer.objects.filter(session=session, question__page=self)
        if not answers:
            for question in self.question_set.all():
                new_answer = Answer()
                new_answer.session = session
                new_answer.question = question
                new_answer.save()


# TODO may need order
class Question(models.Model):
    page = models.ForeignKey(Page)
    text = models.TextField(validators=[MaxLengthValidator(4000)])
    # TODO enum / discriminator
    type = models.CharField(max_length=20)

    def __str__(self):
        return "Question " + str(self.id)


class Choice(models.Model):
    question = models.ForeignKey(Question)
    text = models.CharField(max_length=200)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.text


class Result(models.Model):
    quiz = models.ForeignKey(Quiz)
    score = models.IntegerField(default=0)

    def __str__(self):
        return "Result " + str(self.id) + " Score:" + str(self.score)


class Session(models.Model):
    sid = models.CharField(max_length=200, primary_key=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "Session " + self.sid


class Answer(models.Model):
    session = models.ForeignKey(Session)
    question = models.ForeignKey(Question)

    def __str__(self):
        return "Answer " + str(self.id)

    def evaluate(self):
        is_simple = self.question.type == 'Basic'
        score = 0
        improve = (None, [])
        deteriorate = (None, [])
        selected_choices = self.get_selected_choices()
        for choice in self.question.choice_set.all():
            if choice in selected_choices:
                score += choice.value
            if is_simple:
                if improve[0] is None or choice.value > improve[0]:
                    improve = (choice.value, [choice.id])
                if deteriorate[0] is None or choice.value < deteriorate[0]:
                    deteriorate = (choice.value, [choice.id])
            else:
                improve = self.__improve_multi(improve, choice)
                deteriorate = self.__deteriorate_multi(deteriorate, choice)
        if improve[0] is None or improve[0] == score:
            improve = None
        if deteriorate[0] is None or deteriorate[0] == score:
            deteriorate = None
        return score, improve, deteriorate

    def __deteriorate_multi(self, deteriorate, choice):
        if choice.value < 0:
            if deteriorate[0] is None or deteriorate[0] == 0:
                return (choice.value, [choice.id])
            else:
                deteriorate[1].append(choice.id)
                return (deteriorate[0] + choice.value, deteriorate[1])
        elif choice.value == 0 and deteriorate[0] is None:
            return (choice.value, [choice.id])
        else:
            return deteriorate

    def __improve_multi(self, improve, choice):
        if choice.value > 0:
            if improve[0] is None or improve[0] == 0:
                return (choice.value, [choice.id])
            else:
                improve[1].append(choice.id)
                return (improve[0] + choice.value, improve[1])
        elif choice.value == 0 and improve[0] is None:
            return (choice.value, [choice.id])
        else:
            return improve

    def get_selected_choices(self):
        return [a_s.choice for a_s in self.answerselection_set.all()]


class AnswerSelection(models.Model):
    answer = models.ForeignKey(Answer)
    choice = models.ForeignKey(Choice)

    def __str__(self):
        return "Answer selection" + str(self.id)
