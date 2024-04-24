from django.urls import re_path
from . import views

app_name = 'chats'

urlpatterns = [
    re_path(r'^$', views.Chats.as_view()),
    re_path(r'^latest/(?P<count>[0-9]+)/$', views.LatestChats.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/$', views.ChatDetails.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/typing/$', views.ChatTyping.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/people/$', views.ChatPersonList.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/others/$', views.OtherChatPersonList.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/messages/$', views.Messages.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/messages/(?P<message_id>[0-9]+)/$', views.MessageDetails.as_view()),
    re_path(r'^(?P<chat_id>[0-9]+)/messages/latest/(?P<count>[0-9]+)/$', views.LatestMessages.as_view()),
]
