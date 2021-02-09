from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.home, name='challenge-home'),
    path('register', views.register, name='register'),
    path('join', views.join, name='join-group'),
    path('challenge', views.challenge, name='challenge-match'),
    path('match/<int:match_id>', views.match),
    path('match/<int:match_id>/submit', views.submit_match),
    path('score', views.score, name='scores')
]

urlpatterns += staticfiles_urlpatterns()
