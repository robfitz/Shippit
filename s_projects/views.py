import logging
import simplejson

from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from s_projects.models import Project, STATUS_OPTIONS
from s_stream.models import Update
from s_media.models import Image, Video


def project_info(request, project_id=None):

    statuses = STATUS_OPTIONS

    if request.method == "POST": 
        # TODO: check user is authenticated
        # TODO: check edit permissions

        # ajax save of new project info, create updates if relevant
        project_id = request.POST.get("project", None)
        if project_id:
            project = Project.objects.get(id=project_id)
        else:
            project = Project()

        project.title = request.POST.get("title")
        project.status = request.POST.get("status")
        project.pitch = request.POST.get("pitch")

        new_videos = []
        for key in request.POST:

            if key.startswith('development_video_url'):
                if request.POST.get(key):
                    num = key.split('_')[-1]
                    vid = Video(url=request.POST.get(key),
                            title=request.POST.get("development_video_description_%s" % num, "Development video"))
                    vid.save()
                    new_videos.append(vid)
                    project.development_video_ids.append(vid.id)
                    project.save()

            elif key.startswith('launch_video_url'):
                if request.POST.get(key):
                    logging.info("got a lunch video")
                    num = key.split('_')[-1]
                    vid = Video(url=request.POST.get(key),
                            title=request.POST.get("launch_video_description_%s" % num, "Development video"))
                    vid.save()
                    new_videos.append(vid)
                    logging.info("made a vid: %s" % vid.id)
                    project.launch_video_ids.append(vid.id)
                    project.save()

        thumb_data = request.FILES.get("thumbnail")
        if thumb_data:
            thumbnail = project.thumbnail
            if not thumbnail: 
                thumbnail = Image()
            thumbnail.data = thumb_data
            thumbnail.save() 

            project.thumbnail = thumbnail
            project.save()
            
        logging.info("__*__ bout to check request.files: %s" % request.FILES)
        new_images = []
        for f in request.FILES:
            logging.info("___*___ File: %s" % f)

            if f.startswith("development_media"):
                image = Image(data=request.FILES.get(f))
                image.save()
                project.development_screenshot_ids.append(image.id)
                new_images.append(image)
            elif f.startswith("launch_media"):
                image = Image(data=request.FILES.get(f))
                image.save()
                project.launch_screenshot_ids.append(image.id)
                new_images.append(image)


        project.save()
        if project.id not in request.user.get_profile().owned_project_ids:
            request.user.get_profile().owned_project_ids.append(project.id)
            request.user.get_profile().save()

        if not project_id:
            # create a 'new project' update
            update = Update(type="new project",
                    title="Introducing %s" % project.title,
                    author=request.user,
                    project=project,
                    content=project.pitch[:140],
                    is_published=False)
            update.save()

        if new_images:

            gallery_markdown = ""

            for new_image in new_images:
                gallery_markdown = """%s
<img src='%s' />""" % ( gallery_markdown, new_image.url())

            update = Update(type="screenshots",
                    title="New screenshots",
                    author=request.user,
                    project=project,
                    content=gallery_markdown,
                    is_published=False,
                    order=1)
            update.save()

        if new_videos:
            content = "" 
            i = 0
            for video in new_videos:
                content = "%s<p>%s <a href='%s'>youtube</a></p>" % (content, video.title, video.url)
                i += 1
            update = Update(type="video",
                    title="New video",
                    author=request.user,
                    project=project,
                    content=content,
                    is_published=False,
                    order=2)
            update.save() 

        return HttpResponseRedirect("/project/%s/" % project.id)


    # TODO: check user's edit permissions
    is_edit = request.GET.get("edit", False)
    if not project_id or project_id == "new": 
        is_edit = True

    if request.is_ajax(): 
        project = None
        if project_id:
            project = get_object_or_404(Project, id=project_id) 
        if is_edit:
            return render_to_response("project_edit.html", locals(), context_instance=RequestContext(request))
        else:
            return render_to_response("project.html", locals())

    else:
        proj = project_id
        if not project_id:
            proj = "new"
        url = '/project/%s/' % proj
        if is_edit:
            url = "%s?edit=t" % url
        request.session['info_ajax_url'] = url

        return HttpResponseRedirect("/")
