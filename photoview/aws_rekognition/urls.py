from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tiles$', views.tiles, name='tiles'),
    url(r'^see/([0-9]+)/([0-9]+)$', views.see, name='see'),
    url(r'^see/([0-9]+)/$', views.see, name='see'),
]
