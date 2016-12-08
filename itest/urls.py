"""itest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
import itest.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('apiget.urls')),
    url(r'^charts/', itest.views.charts),
    url(r'^quarterreview', itest.views.quarterreview),
    url(r'^productreview', itest.views.productreview),
    url(r'^feedback', itest.views.feedback),
    url(r'^update', itest.views.update),
    url(r'^download', itest.views.downloadpage),
    url(r'^fbupload', itest.views.uploadpage),
    url(r'^marketshare', itest.views.marketshare),
    url(r'.?',itest.views.home),
]
