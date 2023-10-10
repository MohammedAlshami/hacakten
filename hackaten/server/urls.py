from django.urls import path 
from . import views
from django.conf.urls import handler404


urlpatterns = [ 
    path("register/", views.signup),
    path("login/", views.sign_in),
    path("hub/", views.participant_hub),
    path("cases/", views.case_studies),
    path("groups/", views.grouping),
    path("groups/hub", views.group_hub),
    path("rules/", views.rules),
    path("mentors/", views.mentors),
    path("resources/", views.resources),
    path("submission/", views.submission),
    path("submission/project/", views.project),
    path("submission/project/edit", views.project_edit)

]

# handler404 = views.custom_404
