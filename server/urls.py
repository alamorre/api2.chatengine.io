from django.urls import include, re_path
from django.contrib import admin
from django.urls import path

from django.http import HttpResponse
import os

def health_check(request):
    return HttpResponse(
        f"Welcome to {os.getenv("PIPELINE", 'local')}..", 
        content_type="text/plain"
    )

def trigger_error(request):
    division_by_zero = 1 / 0

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
    path('sentry-debug/', trigger_error),
]
