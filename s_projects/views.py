import logging

from django.shortcuts import get_object_or_404, render_to_response

from s_projects.models import Project


def project_info(request, project_id):

    project = get_object_or_404(Project, id=project_id)

    return render_to_response("project.html", locals())
