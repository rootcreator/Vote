from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("elections/", views.election_list, name="election_list"),
    path("elections/<int:election_id>/vote/", views.vote, name="vote"),
    path("elections/<int:election_id>/results/", views.results, name="results"),
]
