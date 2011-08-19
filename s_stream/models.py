from django.db import models 
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

from s_media.models import Image
from s_users.models import UserProfile
from s_projects.models import Project


class Update(models.Model):

    TYPES = (
            # personal
            ("blog", "Blog"), 
            ("pitch", "Elevator pitch"),

            # development work 
            ("started", "New project started"), 
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

        title_html = "<a href='/blurb/%s/'>%s</a>" % (self.id, trunc_title)

        return title_html



    def to_html(self): 

        if not self.project:
            # personal updates w/ no project
            update_class = 'user'
            update_id = self.author.user.username 

        else:
            update_class = 'project'
            update_id = self.project.id 

        title_html = self.title_html()

        inline_template = get_template("update_attribution_inlines.html")

        return """<div class='update %s' id='%s' name='%s'>
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
            self.type, #endcap class
            self.type, #img class
            self.type, #img url
            self.thumbnail, 
            title_html, 
            inline_template.render(Context({ 'update': self })),
            self.content) 


admin.site.register(Update)
