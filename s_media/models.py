import logging, sys

from django.contrib import admin
from django.db import models
from django.db.models.signals import pre_save

from google.appengine.api import images

from djangotoolbox.fields import BlobField 


class Video(models.Model):

    url = models.CharField(max_length=200)

    timestamp = models.DateTimeField(auto_now_add=True) 

    type = "video"

    title = models.CharField(max_length=140, blank=True, default="")


    def __unicode__(self):
        return "<a href='%s'>%s</a>" % (self.url, self.title)

    def to_html(self):
        logging.info("returning video url: %s"% self.url)
        return "<a href='%s'>%s</a>" % (self.url, self.title)


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


def fix_video_url(sender, instance, raw, **kwargs):

    if not instance.url.startswith("http://"):
        instance.url = "http://%s" % instance.url


pre_save.connect(fix_video_url, sender=Video)


admin.site.register(Image)
admin.site.register(Video)
