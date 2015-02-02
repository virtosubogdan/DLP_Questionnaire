from django.contrib import admin
from quizes.models import Quiz,Page,Result


class PageInLine(admin.StackedInline):
    model = Page
    extra = 2

class QuizAdmin(admin.ModelAdmin):
    inlines = [PageInLine]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Result)
