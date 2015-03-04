from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string


def server_error_404(request):
    return HttpResponse(render_to_string('404.html', {}, RequestContext(request)), status=404)
