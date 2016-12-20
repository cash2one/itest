from django.core.management.base import BaseCommand, CommandError
from _get import getStatCounter

class Command(BaseCommand):
    def handle(self, *args, **options):
        getStatCounter()