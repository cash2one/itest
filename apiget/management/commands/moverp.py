from django.core.management.base import BaseCommand, CommandError
from _get import getStatCounter
from apiget.views import MarketShare, ProductsShare
class Command(BaseCommand):
    def handle(self, *args, **options):
        dbo = MarketShare.objects
        for o in dbo.all():
            touch = dbo.filter(itemname=o.itemname, date=o.date, source=o.source, platform=o.platform, myType=o.myType,
                               market = o.market)
            if touch.count() > 1:
                print o.id + ' repeat'
                print touch.exclude(id=o.id).delete() + ' delete'