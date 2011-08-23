from django.contrib import admin
from django.db import models

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

    def url(self):

        if self.override_url:
            return self.override_url

        else:
            return "/uploads/%s.png" % self.id


    def __unicode__(self):
        return "%s" % self.url()


    def to_html(self):
        return "<a><img class='screenshot' src='%s' /></a>" % self.url()



admin.site.register(Image)
admin.site.register(Video)
