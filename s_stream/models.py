import logging
import string

from django.db import models 
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template
from django.db.models.signals import post_save
from django.core.cache import cache

from s_media.models import Image
from s_users.models import UserProfile
from s_projects.models import Project



class Update(models.Model):

    TYPES = (
            # personal
            ("blog", "Blog"), 
            ("pitch", "Elevator pitch"),

            # development work 
            ("new project", "New project"), 
            ("screenshots", "New screenshots"),
            ("video", "New video"),
            ("milestone", "Development milestone"),
            ("status change", "Project status change"),

            # sucess!
            ("shipped", "Shipped it!"))

    type = models.CharField(choices=TYPES, max_length=20)

    title = models.CharField(max_length=100)

    thumbnail = models.ForeignKey(Image, null=True, blank=True)

    author = models.ForeignKey(UserProfile)

    project = models.ForeignKey(Project, blank=True, null=True)

    content = models.TextField(default="", blank=True)

    is_published = models.BooleanField(default=True)


    def thumb(self):

        if self.thumbnail:
            return self.thumbnail

        elif self.project:
            if self.project.thumbnail:
                return self.project.thumbnail
            else: 
                return '/media/default_project.png'

        elif self.author:
            if self.author.thumbnail:
                return self.author.thumbnail
            else: 
                return '/media/default_user.png'

        else: 
            return '/media/default_update.png'


    def __unicode__(self):

        return "%s - %s (%s by %s)" % (
                self.project,
                self.title,
                self.type,
                self.author)


    def title_html(self):

        trunc_title = self.title
        if len(trunc_title) > 50:
            trunc_title = "%s..." % trunc_title[:27]

        title_html = "<a class='ajax_link' href='/blurb/%s/'>%s</a>" % (self.id, trunc_title)

        return title_html


    def to_html(self): 

        cached = cache.get("update_html_%s" % self.id, "")
        if cached:
            return cached 

        if not self.project:
            # personal updates w/ no project
            update_class = 'user'
            update_id = self.author.user.username 

        else:
            update_class = 'project'
            update_id = self.project.id 

        title_html = self.title_html()

        inline_template = get_template("update_attribution_inlines.html")

        html = """<div class='update %s' id='%s' name='%s'>
    <div class='endcap %s'>
        <img class='%s' src='/media/ui/blurb-%s.png' />
    </div>
    <a><img src='%s' class='thumb' /></a>
    <div class='outer_contents'>
        <h4 class='blurb_title'>%s</h4>
        %s
        <div class='contents'>
            <p>%s</p>
        </div>
    </div> 
</div>
    """ % (update_class,
            update_id, 
            self.id,
            string.replace(self.type, ' ', '-'), #endcap class
            string.replace(self.type, ' ', '-'), #img class
            string.replace(self.type, ' ', '-'), #img url
            self.thumb(), 
            title_html, 
            inline_template.render(Context({ 'update': self })),
            self.content) 

        cache.set("update_html_%s" % self.id, html, 60*60)
        return html

def create_update(sender, instance, created, **kwargs):

    if created: 
        logging.info("%s %s %s" % (instance, instance.project, instance.author))
        if instance.project:
            # attach update to the project it refers to
            instance.project.update_ids.append(instance.id)
            instance.project.save()

        if instance.author:
            # attach update to the user responsible for publishing this 
            instance.author.update_ids.append(instance.id)
            instance.author.save()




post_save.connect(create_update, sender=Update)

admin.site.register(Update)
