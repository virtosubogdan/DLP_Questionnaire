from django.shortcuts import render
from django.http import Http404
from django.views import generic
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

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
    if page_id:
        page = get_not_null(quiz.page_set.get(pk=page_id))
    else:
        page = quiz.get_first_page()
    #import ipdb; ipdb.set_trace()
    if 'previous' in request.POST:
        save_answers_for_page(page, request)
        previous_page = page.previous()
        if previous_page:
            current_page = previous_page
        else:
            current_page = page
    elif 'next' in request.POST:
        save_answers_for_page(page, request)
        next_page = page.next()
        if next_page:
            current_page = next_page
        else:
            current_page = page
    else:
        current_page = page
    request.session['current_page'] = current_page.id;

    #import ipdb; ipdb.set_trace();
    print current_page, current_page.previous(), current_page.next()
    # import ipdb; ipdb.set_trace();
    context = {
        'quiz' : quiz,
        'page' : current_page,
        'not_all_questions_answered' : False,
        'has_previous_page' : not not current_page.previous(),
        'has_next_page' : not not current_page.next()
        }
    return render_to_response('quizes/takeQuiz.html', context, RequestContext(request))

def save_answers_for_page(page, request):
    pass

def start_new_quiz(request):
    del request.session['current_quiz']
    del request.session['current_page']
    return index_view(request)

def get_not_null(obj):
    if not obj:
        raise Http404('Could not find object')
    return obj
