from django.urls import re_path
from . import views

app_name = 'users'

urlpatterns = [
    re_path(r'^me/$', views.MyDetails.as_view()),
    re_path(r'^me/session/$', views.MySession.as_view()),
    re_path(r'^$', views.PeoplePrivateApi.as_view()),
    re_path(r'^search/$', views.SearchOtherUsers.as_view()),
    re_path(r'^session_auth/(?P<session_token>.+)/$', views.SessionTokenAuth.as_view()),
    re_path(r'^(?P<person_id>[0-9]+)/$', views.PersonPrivateApi.as_view()),
]
