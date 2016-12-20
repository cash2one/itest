
from django.core.management.base import BaseCommand, CommandError
from _get import getNetMarketShare

class Command(BaseCommand):
    def handle(self, *args, **options):
        getNetMarketShare()