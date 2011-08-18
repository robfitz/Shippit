from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page 
from django.template import RequestContext

from s_stream.models import Update


@cache_page (1 * 1)
def stream(request):

    updates = Update.objects.all()[:50]

    updates_html = ""
    # turn all updates into html for easy display
    for update in updates:
        updates_html = """%s
%s""" % (updates_html, update.to_html())

    return render_to_response("stream.html", locals(), context_instance=RequestContext(request)) 



def update_info(request, update_id):

    update = get_object_or_404(Update, id=update_id)

    return render_to_response("update.html", locals())
