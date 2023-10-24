""" API v1 URLs. """
from django.urls import re_path

from sanctions.apps.api.v1.views import SanctionsCheckView

app_name = 'v1'
urlpatterns = []

SDN_URLS = [
    re_path(r'^sanctions-check/$', SanctionsCheckView.as_view(), name='sanctions-check'),
]

urlpatterns += SDN_URLS
