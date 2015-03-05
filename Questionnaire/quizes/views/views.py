from django.shortcuts import render
from django.http import Http404
from django.views import generic
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from itertools import ifilter

from quizes.models import Quiz, Result, Question, Session, Answer, AnswerSelection
from quizes.forms import AnswerModelFormSet


S_QUIZ_ID = 'current_quiz'
S_PAGE_ID = 'current_page'
DEFAULT_QUIZ_ID = 1
DEFAULT_PAGE_ID = 1

class IndexView(generic.ListView):
    template_name = 'quizes/index.html'
    context_object_name = 'quizes'

    def get_queryset(self):
        return Quiz.objects.all()


def index_view(request, error=None):
    context = {
        'quizes': Quiz.objects.all(),
        'error': error
    }
    return render_to_response('quizes/index.html', context, RequestContext(request))

def delete_current_answers(request):
    clear_quiz_status(request)
    try:
        Session.objects.get(sid=request.session.session_key).delete()
    except Session.DoesNotExist:
        pass
    return index_view(request)


def continue_quiz(request):
    return take_quiz(request, request.session['current_quiz'])

def get_or_make_session(request):
    try:
       return Session.objects.get(sid=request.session.session_key)
    except Session.DoesNotExist:
        session = Session()
        session.sid = request.session.session_key
        session.save()
        return session

def take_quiz(request, pk):
    session = get_or_make_session(request)
    if 'current_quiz' in request.session:
        if int(request.session['current_quiz']) != int(pk):
            return index_view(request, error='QuizNotFinished')
        page_id = int(request.session['current_page'])
    else:
        page_id = None

    quiz = get_object_or_404(Quiz, pk=pk)
    request.session['current_quiz'] = quiz.id
    all_questions_answered = True
    if page_id:
        page = get_not_null(quiz.page_set.get(pk=page_id))
    else:
        page = quiz.get_first_page()

    if 'previous' in request.POST:
        save_answers_for_page(page, request)
        previous_page = page.previous()
        if previous_page:
            current_page = previous_page
        else:
            current_page = page
    elif 'next' in request.POST:
        if not save_answers_for_page(page, request):
            all_questions_answered = False
            current_page = page
        else:
            next_page = page.next()
            if next_page:
                current_page = next_page
            else:
                current_page = page
    elif 'finish' in request.POST:
        if not save_answers_for_page(page, request):
            all_questions_answered = False
            current_page = page
        else:
            return eval(quiz, request)
    else:
        current_page = page
    request.session['current_page'] = current_page.id

    current_page.make_answers(session)
    formset = AnswerModelFormSet(queryset = Answer.objects.filter(
        session=session, question__page=current_page))
    context = {
        'quiz': quiz,
        'pageNumber': current_page.sequence_number,
        'not_all_questions_answered': not all_questions_answered,
        'has_previous_page': not not current_page.previous(),
        'has_next_page': not not current_page.next(),
        'formset': formset
        }
    return render_to_response('quizes/takeQuiz.html', context, RequestContext(request))


def eval(quiz, request):
    clear_quiz_status(request)
    improvements = []
    deteriorations = []
    total_score = 0
    for page in quiz.page_set.all():
        page_answers = Answer.objects.filter(question__page=page)
        page_improvement = None
        page_deterioration = None
        for answer in page_answers:
            score, improve, deteriorate = answer.evaluate()
            total_score += score
            if improve and (not page_improvement or page_improvement[0][0] < improve[0]):
                page_improvement = (improve, answer.question)
            if deteriorate and (not page_deterioration or page_deterioration[0][0] > deteriorate[0]):
                page_deterioration = (deteriorate, answer.question)
        if page_improvement:
            improvements.append((page_improvement[0][1], page_improvement[1]))
        if page_deterioration:
            deteriorations.append((page_deterioration[0][1], page_deterioration[1]))
    res = Result()
    res.quiz = quiz
    res.score = total_score
    res.save()
    context = {
        'quiz': quiz,
        'score': total_score,
        'improvements': improvements,
        'deteriorations': deteriorations
        }
    return render_to_response('quizes/results.html', context, RequestContext(request))


def save_answers_for_page(page, request):
    missing_answer = False
    form = AnswerModelFormSet(request.POST)
    if not form.is_valid():
        return False
    for form in form.cleaned_data:
        answer, choices = form['id'], form['choices']
        AnswerSelection.objects.filter(answer=answer).delete()
        missing_answer = missing_answer or not choices
        if answer.question.type == 'Basic':
            answer_selection = AnswerSelection()
            answer_selection.answer = answer
            answer_selection.choice = choices
            answer_selection.save()
        else:
            for choice in choices:
                answer_selection = AnswerSelection()
                answer_selection.answer = answer
                answer_selection.choice = choice
                answer_selection.save()
    return not missing_answer


def start_new_quiz(request):
    clear_quiz_status(request)
    return index_view(request)


def clear_quiz_status(request):
    if 'current_quiz' in request.session:
        del request.session['current_quiz']
    if 'current_page' in request.session:
        del request.session['current_page']
    if 'answers' in request.session:
        del request.session['answers']


def get_not_null(obj):
    if not obj:
        raise Http404('Could not find object')
    return obj

def new_take_quiz(request, pk):
    return render(request, 'quizes/newTakeQuiz.html', {'form': None})

