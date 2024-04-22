from django.urls import re_path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    re_path(r'^$', views.Subscriptions.as_view()),
    re_path(r'^(?P<project_id>[\w\-]+)/$', views.CreateSubscription.as_view()),
]
