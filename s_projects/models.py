import logging
from django.contrib import admin

from django.db import models
from djangotoolbox.fields import ListField 

from s_media.models import Image, Video


class Project(models.Model):

    STATUS = (("idea", "A humble idea"),
            ("development", "In development"),
            ("prototype", "Prototyped"),
            ("alpha", "Alpha"),
            ("beta", "Beta"),
            ("shipped", "Shipped"))


    title = models.CharField(max_length=100)

    thumbnail = models.ForeignKey(Image, null=True)

    status = models.CharField(max_length=20, choices=STATUS) 

    screenshot_ids = ListField(models.PositiveIntegerField(), default=[])

    video_ids = ListField(models.PositiveIntegerField(), default=[])

    update_ids = ListField(models.PositiveIntegerField(), default=[])

    pitch = models.TextField()


    def updates(self):

        from s_stream.models import Update

        result = []
        for id in self.update_ids:
            result.append(Update.objects.get(id=id))

        return result 


    def screenshots(self):

        result = []
        for id in self.screenshot_ids:
            result.append(Image.objects.get(id=id))

        return result 


    def __unicode__(self):
        return self.title

admin.site.register(Project)
