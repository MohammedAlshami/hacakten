from django.urls import path, re_path
from . import views
from django.conf.urls import handler404


urlpatterns = [
    path("", views.landing_page),
    # path("register/local", views.signup_local),
    # path("register/sent", views.signup_sent),
    path("register/success", views.form_success),
    # path("register/international", views.signup_international),
    # path("register", views.signup_local),
    path("speakers", views.speakers),
    path("mentors", views.mentors),
    path("judges", views.judges),

    # path("register/verify", views.first_time_verify),

    # path("reset/verify", views.register_verify),
    # path("reset/", views.password_reset),
    # path("reset/confirm", views.password_confirm),
    # path("login/", views.sign_in),
    
    # path("hub", views.participant_hub),
    # path("cases", views.case_studies),
    # path("groups/", views.grouping),
    # path("groups/create", views.group_create),
    # path("groups/join", views.group_join),
    # path("groups/hub", views.group_hub),
    # path("rules", views.rules),
    # path("mentors", views.mentors),
    # path("resources", views.resources),
    # path("submission", views.submission),
    # path("submission/project", views.project),
    # path("submission/project/edit", views.project_edit),
    
]

# handler404 = views.custom_404