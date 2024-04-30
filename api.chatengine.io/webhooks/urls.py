from django.urls import re_path

from . import views

app_name = 'webhooks'

urlpatterns = [
    re_path(r'^$', views.Webhooks.as_view()),
    re_path(r'^test/$', views.WebhookTest.as_view()),
    re_path(r'^(?P<project_id>^([A-Fa-f0-9]{8})(-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12})/$', views.WebhooksWeb.as_view()),
    re_path(r'^(?P<project_id>^([A-Fa-f0-9]{8})(-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12})/(?P<event_trigger>((?:[A-Za-z_ -]|%20)+))/$', views.WebhookDetailsWeb.as_view()),
]
