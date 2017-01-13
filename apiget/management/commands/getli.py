#coding:utf-8
from django.core.management.base import BaseCommand, CommandError
from _get import getLi
import datetime, time

class Command(BaseCommand):
    #该命令的一个选项 --data 日期 可以爬取某日的数据（YYYY-MM-DD） 不加选项默认今天
    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            default=False
        )
    def handle(self, *args, **options):
        if options['date']:
            date = options['date']
            print 'Get ' + date + ' Now'
            getLi(date)
        else:
            nowDate = datetime.datetime.fromtimestamp(time.time() - 3600 * 24)
            endDate = nowDate.strftime('%Y-%m-%d')
            print 'Get ' + endDate + ' Now'
            getLi(endDate)
