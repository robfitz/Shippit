import logging, sys

from django.contrib import admin
from django.db import models

from google.appengine.api import images

from djangotoolbox.fields import BlobField 


class Video(models.Model):

    youtube_id = models.CharField(max_length=20)

    url = models.CharField(max_length=200)

    timestamp = models.DateTimeField(auto_now_add=True) 

    type = "video"


    def __unicode__(self):
        return "<a href='%s'>%s</a>" % (self.url, self.url)

    def to_html(self):

        return "(some video link)"


class Image(models.Model):

    # instead of being uploaded, image is just
    # a link to one hosted elsewhere
    override_url = models.CharField(max_length=200, default="")

    timestamp = models.DateTimeField(auto_now_add=True)

    type = "image"

    # if image is uploaded to our server, here it is
    data = BlobField(blank=True)

    thumbnail_data = BlobField(blank=True, default=None, null=True)


    def thumbnail(self):
        logging.info("### s_media img thumb()")

        if not self.thumbnail_data: 
            try:
                img = images.Image(self.data)
                img.resize(width=100, height=100)
                logging.info("dir img: %s" % dir(img))
                thumb_data = img.execute_transforms(output_encoding=images.PNG)
                self.thumbnail_data = thumb_data
                self.save()
            except:
                logging.info("*** exception getting thumbnail: %s" % sys.exc_info()[0])
                self.thumbnail_data = None
                self.save() 

        if self.thumbnail_data:
            logging.info("### returning thumb data")
            return self.thumbnail_data

        else:
            logging.info("### returning non-thumb data for thumb")
            return self.data

    def url(self):

        if self.override_url:
            return self.override_url

        else:
            return "/uploads/%s.png" % self.id

    def thumb_url(self):

        if self.override_url:
            return self.override_url

        else:
            return "/uploads/%s.thumb.png" % self.id


    


    def __unicode__(self):
        return "%s" % self.url()


    def to_html(self):
        return "<a><img class='screenshot' src='%s' /></a>" % self.url()


admin.site.register(Image)
admin.site.register(Video)
