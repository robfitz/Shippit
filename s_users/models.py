import logging, sys
from django.db import models

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.cache import cache

from djangotoolbox.fields import ListField 

from s_media.models import Image


class InviteCode(models.Model):

    code = models.CharField(max_length=20)


class UserProfile(models.Model):

    user = models.OneToOneField(User)

    thumbnail = models.ForeignKey(Image, null=True)

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


    def owned_projects(self):

        from s_projects.models import Project

        result = []
        for id in self.owned_project_ids:
            result.append(Project.objects.get(id=id))

        return result 


    def contributer_projects(self):

        from s_projects.models import Project

        result = []
        for id in self.contributer_project_ids:
            result.append(Project.objects.get(id=id))

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
        

post_save.connect(create_user_profile, sender=User)

admin.site.register(UserProfile)
