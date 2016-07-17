from django.conf.urls import url
from django.views.decorators.cache import cache_page

from content.views import ItemView
from thromboass_webapp.settings import BASE_VIEW_CACHE_TIME

urlpatterns = [
    url(r'^item/$', cache_page(BASE_VIEW_CACHE_TIME)(ItemView.as_view())),
]
