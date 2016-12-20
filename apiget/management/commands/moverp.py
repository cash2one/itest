from django.core.management.base import BaseCommand, CommandError
from _get import getStatCounter
from apiget.views import MarketShare, ProductsShare
# class MarketShare(models.Model):
#     itemname = models.CharField(max_length=30)
#     value = models.FloatField()
#     date = models.CharField(max_length=10)
#     source = models.TextField()
#     sourcename = models.CharField(max_length=30)
#     platform = models.CharField(max_length=10)# desktop / mobile
#     myType = models.CharField(max_length=10)# browser / os
#     market = models.CharField(max_length=10)# ww / CN
#     remarks = models.TextField()
#
# class ProductsShare(models.Model):
#     productname = models.CharField(max_length=30)
#     pv = models.IntegerField()
#     uv = models.IntegerField()
#     date = models.CharField(max_length=10)
#     datetype = models.CharField(max_length=2)
#     itemname = models.CharField(max_length=30)
#     platform = models.CharField(max_length=10)# ios/android/pc/web
#     myType = models.CharField(max_length=10)# browser / os / dpi
#     remarks = models.TextField()
class Command(BaseCommand):
    def handle(self, *args, **options):
        dbo = MarketShare.objects
        for o in dbo.all():
            touch = dbo.filter(itemname=o.itemname, date=o.date, source=o.source, platform=o.platform, myType=o.myType,
                               market = o.market)
            if touch.count() > 1:
                print o.id + ' repeat'
                print touch.exclude(id=o.id).delete() + ' delete'