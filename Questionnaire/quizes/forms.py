from django import forms
from django.forms.models import ModelMultipleChoiceField
from django.forms.models import modelformset_factory

from quizes.models import Page, Question, Quiz, Choice, Answer


class AnswerModelForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ()

    def __init__(self, *args, **kwargs):
        super(AnswerModelForm, self).__init__(*args, **kwargs)
        question = self.instance.question
        selected_choices = self.instance.get_selected_choices()
        if question.type == 'Basic':
            field = forms.ModelChoiceField(
                required=True, widget=forms.RadioSelect, empty_label=None,
                queryset = Choice.objects.filter(question=question))
            if len(selected_choices) == 1:
                field.initial = selected_choices[0].id
        else:
            field = forms.ModelMultipleChoiceField(
                required=True, widget=forms.CheckboxSelectMultiple,
                queryset = Choice.objects.filter(question=question))
            field.initial = [s_c.id for s_c in selected_choices]

        self.fields['choices'] = field
        field.label = question.text

AnswerModelFormSet = modelformset_factory(Answer, form=AnswerModelForm, extra=0)
