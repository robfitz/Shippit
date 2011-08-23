import logging, sys

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page 
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache

from s_stream.models import Update


def stream(request):
    
    # sometimes stream is called via a redirect, in which
    # case the session remembers which ajax to load in
    try: 
        info_ajax_url = request.session['info_ajax_url']
        # clear it after retrieving to avoid screwing up all navigation
        del request.session['info_ajax_url']
    except:
        info_ajax_url = None

    logging.info("XXX got info_ajax_url: %s" % info_ajax_url)


    unconfirmed_updates_html = ""
    updates_html = cache.get("updates_html", "")

    if request.user.is_authenticated():
        for unconfirmed in Update.objects.filter(is_published=False, author=request.user.get_profile()):
            unconfirmed_updates_html = """%s %s""" % (update.to_html(), unconfirmed_updates_html) 

    if not updates_html: 
        updates = Update.objects.all()[:50]

        # turn all updates into html for easy display
        for update in updates:
            if update.is_published:
                updates_html = """%s
    %s""" % (update.to_html(), updates_html)

    show_no_invite_alert = False
    if 'no_invite' in request.session:
        # del request.session['no_invite']
        show_no_invite_alert = True 

    cache.set("updates_html", updates_html, 60*1)

    return render_to_response("stream.html", locals(), context_instance=RequestContext(request)) 


def publish_unconfirmed(request, update_id):
    try:
        update = Update.objects.get(id=update_id)
    
        if update.is_published:
            return HttpResponse("error: update %s has already been confirmed" % update_id)
        elif (not request.user.is_authenticated()) or update.author.user != request.user:
            return HttpResponse("error: no permissions")
        else:
            update.is_published = True
            update.save()
            return HttpResponse("ok")
    except:
        logging.info(sys.exc_info()[0])
        return HttpResponse("error: update %s does not exist" % update_id)

def discard_unconfirmed(request, update_id):
    try:
        update = Update.objects.get(id=update_id)
    
        if update.is_published:
            return HttpResponse("error: update %s has already been confirmed" % update_id)
        elif (not request.user.is_authenticated()) or update.author.user != request.user:
            return HttpResponse("error: no permissions")
        else:
            update.delete()
            return HttpResponse("ok")
    except:
        logging.info(sys.exc_info()[0])
        return HttpResponse("error: update %s does not exist" % update_id)



def update_info(request, update_id):

    update = get_object_or_404(Update, id=update_id)

    if update.type == "new project" or update.type == "pitch":

        # updates about a new project don't have their own content,
        # but rather link straight to the project in question
        return HttpResponseRedirect("/project/%s/" % update.project.id)

    return render_to_response("update.html", locals())
