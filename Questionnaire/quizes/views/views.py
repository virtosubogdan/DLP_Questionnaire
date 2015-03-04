from django.shortcuts import render
from django.http import Http404
from django.views import generic
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from itertools import ifilter

from quizes.models import Quiz

S_QUIZ_ID = 'current_quiz'
S_PAGE_ID = 'current_page'
DEFAULT_QUIZ_ID = 1
DEFAULT_PAGE_ID = 1

# BV_Q: how to use ListView instead of index_view ?
class IndexView(generic.ListView):
    template_name = 'quizes/index.html'
    context_object_name = 'quizes'

    def get_queryset(self):
        return Quiz.objects.all()

def index_view(request, error=None):
    context = {
        'quizes' : Quiz.objects.all(),
        'error' : error
    }
    return render_to_response('quizes/index.html', context, RequestContext(request))

# BV_Q: how to use DetailView instead of take_quiz ?
class TakeQuiz(generic.DetailView):
    template_name = 'quizes/takeQuiz.html'
    model = Quiz

#    def get_context_data(self, *args, **kwargs):
#        import ipdb; ipdb.set_trace()
#        return None

#    def get_queryset(self, *args, **kwargs):
#        import ipdb; ipdb.set_trace()
#        return None

def continue_quiz(request):
    return take_quiz(request, request.session['current_quiz'])

def take_quiz(request, pk):
    print 'take_quiz', pk
    if 'current_quiz' in request.session:
        if int(request.session['current_quiz']) != int(pk):
            print 'wrong quiz id ', request.session['current_quiz']
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
        request.session['answers'] = {}
    # import ipdb; ipdb.set_trace()
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
            current_page =  page
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
            return eval(quiz,request.session.get('answers',{}),request)
    else:
        current_page = page
    request.session['current_page'] = current_page.id;

    #import ipdb; ipdb.set_trace();
    print 'answers', request.session.get('answers',{})
    print 'pages', current_page, current_page.previous(), current_page.next()
    context = {
        'quiz' : quiz,
        'questions' : prepare_for_render(current_page, request.session.get('answers',{}).
                                         get(str(current_page.id),{})),
        'pageNumber' : current_page.sequence_number,
        'not_all_questions_answered' : not all_questions_answered,
        'has_previous_page' : not not current_page.previous(),
        'has_next_page' : not not current_page.next()
        }
    return render_to_response('quizes/takeQuiz.html', context, RequestContext(request))

def eval(quiz, answers, request):
    clear_quiz_status(request)
    context = {
        'quiz' : quiz,
        'score' : 0,
        'avg_score' : 0,
        'improvements' : [],
        'deteriorations' : []
        }
    return render_to_response('quizes/results.html', context, RequestContext(request))

def save_answers_for_page(page, request):
    if 'answers' not in request.session:
        request.session = {}
    page_answers = request.session['answers'].get(str(page.id),{})
    missing_answer = False
    for question in page.question_set.all():
        if question.type == 'Basic':
            if str(question.id) in request.POST:
                page_answers[str(question.id)] = [int(request.POST.get(str(question.id)))]
            else:
                page_answers[str(question.id)] = []
                missing_answer = True
        else:
            prefix = str(question.id) + 'c'
            tmp = [int(key[len(prefix):]) for key in request.POST.keys() if key.startswith(prefix)]
            page_answers[str(question.id)] = tmp
            missing_answer = missing_answer or not tmp
    request.session['answers'][str(page.id)] = page_answers
    request.session.modified = True
    return not missing_answer

def prepare_for_render(page, answers):
    questions = []
    print 'prepare',page.id,answers
    for question in page.question_set.all():
        choices = []
        isMultiChoice = question.type == 'Multiple'
        selected_choices = answers.get(str(question.id),{})
        for choice in question.choice_set.all():
            print choice.id, selected_choices
            choices.append([choice.text, choice.id,
                            str(question.id)+'c'+str(choice.id) if isMultiChoice else
                            str(question.id), choice.id in selected_choices])
        questions.append([question.id, question.text, choices])
    print questions
    return questions

def start_new_quiz(request):
    clear_quiz_status(request)
    return index_view(request)

def clear_quiz_status(request):
    del request.session['current_quiz']
    del request.session['current_page']
    del request.session['answers']

def get_not_null(obj):
    if not obj:
        raise Http404('Could not find object')
    return obj

