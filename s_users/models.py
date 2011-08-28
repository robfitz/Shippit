import logging, sys
from django.db import models

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.core.cache import cache

from djangotoolbox.fields import ListField 

from s_media.models import Image
from utils.util import str_to_array


class InviteCode(models.Model):

    code = models.CharField(max_length=20)

    quantity = models.PositiveIntegerField(default=1)


    def __unicode__(self):
        return "%sx %s" % (self.quantity, self.code)

class UserProfile(models.Model):

    user = models.OneToOneField(User)

    thumbnail = models.ForeignKey(Image, null=True, blank=True)

    signup_date = models.DateTimeField(auto_now_add=True, null=True)

    update_ids = ListField(models.PositiveIntegerField(), default=[])
    owned_project_ids = ListField(models.PositiveIntegerField(), default=[])
    contributer_project_ids = ListField(models.PositiveIntegerField(), default=[]) 

    invite_appeal = models.TextField(blank=True, default="")

    about = models.TextField(blank=True, default="")

    def __unicode__(self):
        return self.user.username


    def all_project_ids(self):
        all = list(self.contributer_project_ids)
        all.extend(self.owned_project_ids)
        return all

    def all_projects(self):

        logging.info("*** all projects"  )

        all = list(self.owned_projects())
        all.extend(self.contributer_projects())
        logging.info("*** all projects: %s" % all)
        return all 
    

    def owned_projects(self):

        from s_projects.models import Project

        result = []
        to_delete = []
        i = 0
        for id in self.owned_project_ids:
            try:
                result.append(Project.objects.get(id=id))
            except:
                to_delete.append(i)
            i += 1

        if to_delete:
            i = 0
            for to_del in to_delete:
                del self.owned_project_ids[to_del - i]
                i += 1 
            self.save()

        return result 


    def contributer_projects(self):

        from s_projects.models import Project

        result = []
        to_delete = []
        i = 0
        for id in self.contributer_project_ids:
            try:
                logging.info("&&& trying to get projet id:%s" % id)
                result.append(Project.objects.get(id=id))
            except:
                to_delete.append(i)
            i += 1

        if to_delete:
            i = 0
            for to_del in to_delete:
                del self.contributer_project_ids[to_del - i]
                i += 1 
            self.save()

        logging.info("&&&& contrib projects: %s" % result)

        return result 


    def updates(self):

        from s_stream.models import Update

        to_delete = []
        ups = []
        i = 0
        logging.info("user update ids: %s" % self.update_ids)
        for id in self.update_ids:
            try: 
                update = Update.objects.get(id=id)
                logging.info("got update: %s" % update)
                ups.append(update)
            except:
                # update no longer exists, ignore
                logging.info("to delete appended: %s" % i)
                to_delete.append(i)
            i += 1

        if to_delete:
            logging.info("*** to del from user: %s" % to_delete)
            i = 0
            for to_del in to_delete:
                del self.update_ids[to_del - i]
                i += 1 
            self.save()

        return ups 

def create_user_profile(sender, instance, created, **kwargs):

    if created:

        # extra info
        profile = UserProfile.objects.create(user=instance)

    for update_id in instance.get_profile().update_ids:
        cache.delete("update_html_%s" % update_id)
        

def clean_listfields(sender, instance, raw, **kwargs):
    
    if instance.owned_project_ids.__class__ != list:
        instance.owned_project_ids = str_to_array(instance.owned_project_ids)

    if instance.contributer_project_ids.__class__ != list:
        instance.contributer_project_ids = str_to_array(instance.contributer_project_ids)

    if instance.update_ids.__class__ != list:
        instance.update_ids = str_to_array(instance.update_ids)


post_save.connect(create_user_profile, sender=User)
pre_save.connect(clean_listfields, sender=UserProfile)

admin.site.register(UserProfile)
admin.site.register(InviteCode)
