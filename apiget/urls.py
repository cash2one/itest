from django.conf.urls import url
import apiget.views

urlpatterns = [
    url(r'^reset/', apiget.views.HolesResetAPI),
    url(r'^get/', apiget.views.HoleGetAPI),
    url(r'^search', apiget.views.HoleSelectAPI),
    url(r'^detailbyid', apiget.views.HoleDetailAPI),
    url(r'^productnamelist', apiget.views.ProducnNameAPI),
    url(r'.?',apiget.views.home),
]
