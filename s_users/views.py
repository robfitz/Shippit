import logging
from datetime import datetime

from django.contrib import auth 
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse 
from django.contrib.auth.models import User

from s_broadcast.models import Subscription
from s_users.models import InviteCode
from s_media.models import Image


def user_info(request, username):

    user = get_object_or_404(User, username=username)

    if request.method == "POST":
        if request.user != user and not request.user.is_staff:
            return HttpResponse("error: no user edit permissions")

        user.username = request.POST.get("username")
        user.save()

        user.get_profile().about = request.POST.get("about")
        user.get_profile().save()

        thumb_data = request.FILES.get("thumbnail")
        if thumb_data:
            thumbnail = user.get_profile().thumbnail
            if not thumbnail: 
                thumbnail = Image()
            thumbnail.data = thumb_data
            thumbnail.save() 

            user.get_profile().thumbnail = thumbnail
            user.get_profile().save() 

        return HttpResponseRedirect("/user/%s/" % user.username)

    is_edit = request.GET.get("edit", False)
    if request.user != user and not request.user.is_staff:
        is_edit = False

    if not request.is_ajax():

        url = '/user/%s/' % user.username
        if is_edit:
            url = "%s?edit=t" % url
        request.session['info_ajax_url'] = url

        return HttpResponseRedirect("/")

    if is_edit:
        return render_to_response("profile_edit.html", locals(), context_instance=RequestContext(request))

    else:
        return render_to_response("profile.html", locals())


def register(request):

    next = "/"
    errors = ""

    if request.method == "POST":

        username = request.POST.get("username")

        if User.objects.filter(username=username).exists():
            errors = "That username has already been taken. If that's your account, try logging in instead. Otherwise, try creating an account with a different username"
            logging.info("&&& register username taken")

        else:
            pw1 = request.POST.get("password_1")
            pw2 = request.POST.get("password_2") 

            if pw1 and pw1 != pw2:
                errors = "Passwords don't match. Typo?"
                logging.info("&&& register PW don't match")

            else:

                try:
                    invite = InviteCode.objects.get(code=request.POST.get("invite_code")) 
                except:
                    invite = None

                email = request.POST.get("email", "")
                user = User.objects.create_user(username, email=email, password=pw1)
                user = auth.authenticate(username=username, password=pw1)
                if user and invite: 
                    # use up the invite
                    invite.delete()

                    auth.login(request, user) 

                    logging.info("&&& got invite %s and returning new user success")
                    return HttpResponseRedirect(request.POST.get("next"))

                elif user and not invite:

                    # no invitation
                    user.is_active = False
                    user.save()

                    request.session['no_invite'] = user.username

                    logging.info("&&& set no_invite and is_active = False")

                    return HttpResponseRedirect('/') 
                else:
                    logging.info("&&& registration failed unexpectedly")


    logging.info("&&& returning registration fields")
    return render_to_response("registration/register.html", locals(), context_instance=RequestContext(request))


def request_invite(request):

    if not 'no_invite' in request.session:
        # this is bad, since they haven't yet
        # been rejected for an account, so shouldn't
        # be able to request anything
        return HttpResponse("error: no attempted signup")

    username = request.session['no_invite']
    user = None
    try:

        # clear session so they aren't
        # annoyed every page load w/ prompt
        del request.session['no_invite']

        user = User.objects.get(username=username)
        user.get_profile().invite_appeal = request.POST.get("appeal", "")
        user.get_profile().save()

        subscription, created = Subscription.objects.get_or_create(title="invite_request")
        subscription.subscribe(user.email)

        return HttpResponse("ok")

    except:
        return HttpResponse("error: matching user not found") 


def reject_invite(request):
    
    # clear session so they aren't
    # annoyed every page load w/ prompt
    del request.session['no_invite']

    return HttpResponse("ok")

