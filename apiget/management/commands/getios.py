from django.core.management.base import BaseCommand, CommandError
from _get import getIos

class Command(BaseCommand):
    def handle(self, *args, **options):
        getIos()