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

        result = []
        for id in self.update_ids:
            result.append(Update.objects.get(id=id))

        return result 

def create_user_profile(sender, instance, created, **kwargs):

    if created:

        # extra info
        profile = UserProfile.objects.create(user=instance)

    for update_id in instance.get_profile().update_ids:
        cache.delete("update_html_%s" % update_id)
        

post_save.connect(create_user_profile, sender=User)

admin.site.register(UserProfile)
