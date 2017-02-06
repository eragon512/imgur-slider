from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^album/$', views.album_list, name='album_list'),
    url(r'^album/(?P<album_id>[A-Za-z0-9_-]*$)', views.album, name='album'),
    url(r'^album/view/(?P<album_id>[A-Za-z0-9_-]*$)', views.view_album, name='view_album'),
]
