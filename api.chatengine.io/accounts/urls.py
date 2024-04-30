from django.urls import re_path
from . import views

app_name = 'accounts'

urlpatterns = [
    re_path(r'^$', views.Accounts.as_view()),
    re_path(r'^me/$', views.MyDetails.as_view()),
    re_path(r'^login/$', views.CustomObtainAuthToken.as_view()),
    re_path(r'^mfa/$', views.MultiFactorLogin.as_view()),
    re_path(r'^(?P<reset_uuid>^([A-Fa-f0-9]{8})(-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12})/$', views.ResetAccount.as_view()),
]
