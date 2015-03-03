from django.contrib import admin
from django.forms.models import ModelForm
from quizes.models import Quiz,Page,Result,Question,Choice

# TODO wrong, must change
class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        return True

class PageInLine(admin.StackedInline):
    model = Page
    extra = 1
    form = AlwaysChangedModelForm

class ResultstInLine(admin.StackedInline):
    model = Result
    extra = 0

class QuizAdmin(admin.ModelAdmin):
    inlines = [PageInLine, ResultstInLine]

class ChoiceInLine(admin.StackedInline):
    model = Choice

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInLine]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
