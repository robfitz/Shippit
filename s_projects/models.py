import logging, sys
from django.contrib import admin

from django.db import models
from djangotoolbox.fields import ListField 
from django.db.models.signals import pre_save, post_save, pre_delete
from django.core.cache import cache

from s_media.models import Image, Video

from utils.util import str_to_array


STATUS_OPTIONS = (("idea", "A humble idea"),
        ("development", "In development"),
        ("prototype", "Prototyped"),
        ("alpha", "Alpha"),
        ("beta", "Beta"),
        ("shipped", "Shipped"))


class Project(models.Model):

    temp_tags = ListField(models.CharField(max_length=20), default=[]) 

    title = models.CharField(max_length=100)

    thumbnail = models.ForeignKey(Image, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_OPTIONS) 

    development_video_ids = ListField(models.PositiveIntegerField(), default=[])

    launch_screenshot_ids = ListField(models.PositiveIntegerField(), default=[])

    launch_video_ids = ListField(models.PositiveIntegerField(), default=[])

    development_screenshot_ids = ListField(models.PositiveIntegerField(), default=[])

    update_ids = ListField(models.PositiveIntegerField(), default=[])

    pitch = models.TextField(blank=True)


    def remove_update(self, update):

        i = 0
        for id in self.update_ids:
            if id == update.id:
                del self.update_ids[i]
                self.save()
                return True
            i += 1
        return False 


    def updates(self):

        from s_stream.models import Update

        to_delete = []
        result = []
        i = 0
        for id in self.update_ids:
            try:
                update = Update.objects.get(id=id)
                result.append(update)
            except:
                # update no longer exists, ignore
                pass 
            i += 1

        if to_delete:
            i = 0
            for to_del in to_delete:
                del self.update_ids[to_del - i]
                i += 1 
            self.save()

        return result


    def launch_media(self):

        result = []
        for id in self.launch_screenshot_ids:
            result.append(Image.objects.get(id=id))

        for id in self.launch_video_ids:
            result.append(Video.objects.get(id=id))

        return result


    def development_media(self):

        result = []
        for id in self.development_screenshot_ids:
            result.append(Image.objects.get(id=id))

        for id in self.development_video_ids:
            result.append(Video.objects.get(id=id))

        return result


    def __unicode__(self):
        return self.title




# list fields are horrific in the admin, so saving
# a model causes the array to turn into a string.
# this is a temporary workaround until the full
# admin fix can be implemented
def clean_listfields(sender, instance, raw, **kwargs):
    logging.info("cleanlistfields")
    
    if instance.development_screenshot_ids.__class__ != list:
        instance.development_screenshot_ids = str_to_array(instance.development_screenshot_ids)

    if instance.development_video_ids.__class__ != list:
        instance.development_video_ids = str_to_array(instance.development_video_ids)
    
    if instance.launch_screenshot_ids.__class__ != list:
        instance.launch_screenshot_ids = str_to_array(instance.launch_screenshot_ids)

    if instance.launch_video_ids.__class__ != list:
        instance.launch_video_ids = str_to_array(instance.launch_video_ids)

    if instance.update_ids.__class__ != list:
        instance.update_ids = str_to_array(instance.update_ids)




def save_project(sender, instance, created, **kwargs):

    for update_id in instance.update_ids:
        cache.delete("update_html_%s" % update_id)


def project_deleted(sender, instance, **kwargs):

    from s_stream.models import Update

    for update_id in instance.update_ids:
        try:
            update = Update.objects.get(id=update_id)
            update.delete()
            logging.info("success")
        except:
            pass 


pre_save.connect(clean_listfields, sender=Project)
post_save.connect(save_project, sender=Project)
pre_delete.connect(project_deleted, sender=Project)

admin.site.register(Project)
