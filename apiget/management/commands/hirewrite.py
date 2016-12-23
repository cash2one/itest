from django.core.management.base import BaseCommand, CommandError
from apiget.views import _dblog, _HoleSave, _HoleGet, _HoleDelete
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        _HoleDelete()
        jtest = _HoleGet()
        for hi in jtest['holeInfos']:
            _HoleSave(hi)
            print hi['id']
        _dblog('Reset holeinfo at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))