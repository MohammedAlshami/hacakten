from django.urls import path 
from . import views


urlpatterns = [ 
    path("", views.signup),
    path("hub/", views.participant_hub),
    path("cases/", views.case_studies),
    path("groups/", views.grouping),
    path("rules/", views.rules),
    path("mentors/", views.mentors),
    path("resources/", views.resources),
    path("submission/", views.submission)
]