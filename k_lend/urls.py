"""
URL configuration for k_lend project.
"""
from django.urls import path, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path('', include('k_lend_app.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('dev-admin/', admin.site.urls),
    ]
