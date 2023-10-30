""" API v1 URLs. """
from django.urls import re_path

from sanctions.apps.api.v1.views import SDNCheckView

app_name = 'v1'
urlpatterns = []

SDN_URLS = [
    re_path(r'^sdn-check/$', SDNCheckView.as_view(), name='sdn-check'),
]

urlpatterns += SDN_URLS
