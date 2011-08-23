import logging

from django.http import HttpResponseRedirect, HttpResponse

from s_media.models import Image

def get_uploaded_image(request, id):

    toks = id.split('.')
    id = toks[0]

    try:
        image = Image.objects.get(id=id)
        data = image.data
    except:
        data = None

    if not data:
        return HttpResponseRedirect('/media/default_image.png')

    return HttpResponse(data, content_type='application/octet-stream')
