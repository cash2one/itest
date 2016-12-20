from django.core.management.base import BaseCommand, CommandError
from _get import getAndroid

class Command(BaseCommand):
    def handle(self, *args, **options):
        getAndroid()