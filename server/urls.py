from django.urls import include, re_path
from django.contrib import admin
from django.urls import path

from django.http import HttpResponse
import os

from server.utils.redis import RedisClient

r = RedisClient()

def health_check(request):
    key = 'test'
    r.client.set(key, 'pass')
    value = r.client.get(key)
    r.client.delete(key)
    return HttpResponse(
        f"Pipelene: {os.getenv("PIPELINE", 'local')}\nRedis: {value}", 
        content_type="text/plain"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^accounts/', include('accounts.urls', namespace='accounts')),
    re_path(r'^projects/', include('projects.urls', namespace='projects')),
    re_path(r'^users/', include('users.urls', namespace='users')),
    re_path(r'^chats/', include('chats.urls', namespace='chats')),
    re_path(r'^crons/', include('crons.urls', namespace='crons')),
    re_path(r'^webhooks/', include('webhooks.urls', namespace='webhooks')),
    re_path(r'^subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    # Health check
    path('', health_check, name='health_check'),
    path('health/', health_check, name='health_check'),
]
