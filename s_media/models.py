from django.contrib import admin
from django.db import models


class Video(models.Model):

    youtube_id = models.CharField(max_length=20)

    url = models.CharField(max_length=200)

    timestamp = models.DateTimeField(auto_now_add=True) 


    def __unicode__(self):
        return "<a href='%s'>%s</a>" % (self.url, self.url)


class Image(models.Model):

    url = models.CharField(max_length=200, default="")

    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s" % self.url



admin.site.register(Image)
admin.site.register(Video)
