from django.core.management.base import BaseCommand, CommandError
from _get import getBaidu, getBaiduNew

class Command(BaseCommand):
    def handle(self, *args, **options):
        getBaidu()
        getBaiduNew()