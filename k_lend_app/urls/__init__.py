# =================================
# Lend App URL Configuration
# =================================
from django.urls import include, path
from . import urls_browser

app_name = "k_lend_app"

urlpatterns = [
    path("", include(urls_browser)),
]