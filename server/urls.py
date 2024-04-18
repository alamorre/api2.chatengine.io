from django.urls import include, re_path
from django.contrib import admin
from django.urls import path

from django.http import HttpResponse
import os

def health_check(request):
    return HttpResponse(
        f"Welcome to {os.getenv("PIPELINE", 'local')}!", 
        content_type="text/plain"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^accounts/', include('accounts.urls', namespace='accounts')),
    # Health check
    path('', health_check, name='health_check'),
]
