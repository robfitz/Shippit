import logging, sys

from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.cache import cache_page

from s_media.models import Image 


@cache_page ( 60 * 60 * 24 )
def get_uploaded_image(request, id):

    toks = id.split('.')
    id = toks[0]

    try:
        image = Image.objects.get(id=id)
        data = image.data
        if toks[1] == 'thumb':
            logging.info("get_uploaded trying for thumb")
            data = image.thumbnail()
            logging.info("got a thumb!")
    except:
        logging.info("no data: %s" % sys.exc_info()[0])
        data = None

    if not data:
        return HttpResponseRedirect('/media/default_image.png')

    return HttpResponse(data, content_type='image/png')
