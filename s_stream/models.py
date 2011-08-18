from django.db import models 
from django.contrib import admin

from s_media.models import Image
from s_users.models import UserProfile
from s_projects.models import Project


class Update(models.Model):

    TYPES = (
            # personal
            ("blog", "Blog"), 
            ("elevator pitch", "Elevator pitch"),

            # development work 
            ("project started", "New project started"), 
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


        if not self.project:

            title_html = "<a href='/blurb/%s/'>%s</a>" % (self.id, self.title)

        else: 
            title_html = "<a href='/project/%s/'>%s</a> - <a href='/blurb/%s/'>%s</a>" % (self.project.id,
                        self.project.title,
                        self.id,
                        self.title)

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


        return """<div class='update %s' id='%s' name='%s'>
    <a><img src='%s' class='thumb' /></a>
    <div class='contents'>
        <h4 class='blurb_title'>%s</h4>
        <p>%s</p>
    </div> 
</div>
    """ % (update_class,
            update_id, 
            self.id,
            self.thumbnail, 
            title_html, 
            self.content) 


admin.site.register(Update)
