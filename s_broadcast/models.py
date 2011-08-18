from django.db import models
from django.contrib import admin

from djangotoolbox.fields import ListField 


class Subscription(models.Model):

    title = models.CharField(max_length=50)

    subscribers = ListField(models.EmailField(max_length=100), default=[])


    def subscribe(self, email):

        if not email:
            return False

        if email not in self.subscribers:
            self.subscribers.append(email)

            self.save()

        return True


    def __unicode__(self):

        return self.title


admin.site.register(Subscription)
