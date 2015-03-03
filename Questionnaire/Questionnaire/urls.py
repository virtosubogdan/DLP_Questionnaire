from django.conf.urls import patterns, include, url
from django.contrib import admin

from quizes.views import views, errors

# Error views
handler404 = 'quizes.views.errors.server_error_404'

urlpatterns = patterns(
    '',
    # Examples:
    url(r'^$', views.IndexView.as_view(), name='home'),
    url(r'^(?P<pk>\d+)/quiz$', views.take_quiz, name='takeQuiz'),
    url(r'^startNewQuiz$', views.start_new_quiz, name='startNewQuiz'),
    url(r'^continueQuiz$', views.continue_quiz, name='continueQuiz'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^error404$', errors.server_error_404, name='error404'),

    url(r'^admin/', include(admin.site.urls)),
)
