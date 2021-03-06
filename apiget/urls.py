from django.conf.urls import url
import apiget.views

urlpatterns = [
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
    url(r'^getordergroup', apiget.views.GetOrderGroupsAPI),
    url(r'^getvt', apiget.views.GetVulTypeAPI),
    url(r'^update', apiget.views.TIUpdate),
    url(r'^download', apiget.views.FileDownloadAPI),
    url(r'^filename', apiget.views.GetFileNameAPI),
    url(r'^fbupload', apiget.views.FBUploadAPI),
    url(r'^getpsfi', apiget.views.GetPSFormItem),

    url(r'^getms',apiget.views.GetMarketShareAPI),
    url(r'^getps', apiget.views.GetProductShareAPI),
]
