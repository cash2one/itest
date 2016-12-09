from django.conf.urls import url
import apiget.views

urlpatterns = [
    url(r'^reset/', apiget.views.HolesResetAPI),
    url(r'^search', apiget.views.HoleTableAPI),
    url(r'^detailbyid', apiget.views.HoleDetailAPI),
    url(r'^productnamelist', apiget.views.ProductNameAPI),
    url(r'^statistics', apiget.views.StatisticsAPI),
    url(r'^update/', apiget.views.HolesUpdateAPI),
    url(r'^quarterbugs', apiget.views.QuartersBugsAPI),
    url(r'^productbugs', apiget.views.ProductBugsAPI),
    url(r'^feedback', apiget.views.FeedBackAPI),
    url(r'^getquarters', apiget.views.GetQuartersAPI),
    url(r'^getlastentry', apiget.views.GetLastEntryAPI),
    url(r'^update', apiget.views.TIUpdate),
    url(r'^download', apiget.views.FileDownloadAPI),
    url(r'^filename', apiget.views.GetFileNameAPI),
    url(r'^fbupload', apiget.views.FBUploadAPI),
    url(r'^getsc',apiget.views.getStatCounter),
    url(r'^getnms',apiget.views.initNetMarketShare),
    url(r'^getms',apiget.views.GetMarketShareAPI),
    url(r'^getandroid', apiget.views.getAndroid),
    url(r'^getbaidu', apiget.views.getBaidu),
    url(r'^getios', apiget.views.getIos),
]
