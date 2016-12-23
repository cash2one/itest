from __future__ import unicode_literals

from django.db import models

# Create your models here.
class information(models.Model):
    Name = models.CharField(max_length=30)
    Data = models.TextField()
    Class = models.CharField(max_length=10)
    def __unicode__(self):
        return self.Name

class HoleInfo(models.Model):
    status = models.CharField(max_length=2)
    targetType = models.CharField(max_length=10)
    scanType = models.CharField(max_length=2)
    description = models.TextField()
    level = models.CharField(max_length=2)
    createTime = models.BigIntegerField()
    checkResult = models.BooleanField()
    updateStatus = models.CharField(max_length=2)
    productName = models.CharField(max_length=50)
    vulType = models.CharField(max_length=50)
    groupName = models.CharField(max_length=10)
    h_id = models.CharField(max_length=20)
    targets = models.TextField()
    quarter = models.CharField(max_length=10)


class TestInfos(models.Model):
    quarter = models.CharField(max_length=8)
    group = models.CharField(max_length=20)
    bugs_found = models.CharField(max_length=8)
    bugs_found_p1 = models.CharField(max_length=8)
    bugs_escape = models.CharField(max_length=8)
    bugs_escape_noduty = models.CharField(max_length=8)
    bugs_escape_p1 = models.CharField(max_length=8)
    bugs_escape_p1_noduty = models.CharField(max_length=8)
    bugs_escape_info = models.TextField()
    bugs_found_function = models.CharField(max_length=8)
    bugs_found_function_p1 = models.CharField(max_length=8)
    bugs_other = models.CharField(max_length=8)
    bugs_other_p1 = models.CharField(max_length=8)

    allow_tests = models.CharField(max_length=8)
    allow_tests_pass = models.CharField(max_length=8)

    t_id = models.CharField(max_length=8)


class FeedBack(models.Model):
    date = models.CharField(max_length=16)
    name = models.CharField(max_length=10)
    group = models.CharField(max_length=10)
    grade1 = models.FloatField()
    grade2 = models.FloatField()

    feedback = models.TextField()
    feedback_done = models.CharField(max_length=2)

    need_machine = models.CharField(max_length=2)
    need_person = models.CharField(max_length=2)
    bug_qua = models.CharField(max_length=2)
    suggest = models.CharField(max_length=2)
    good = models.CharField(max_length=2)
    process = models.CharField(max_length=2)
    chat = models.CharField(max_length=2)
    escape1 = models.CharField(max_length=2)

class MarketShare(models.Model):
    itemname = models.CharField(max_length=30)
    value = models.FloatField()
    date = models.CharField(max_length=10)
    source = models.TextField()
    sourcename = models.CharField(max_length=30)
    platform = models.CharField(max_length=10)# desktop / mobile
    myType = models.CharField(max_length=10)# browser / os
    market = models.CharField(max_length=10)# ww / CN
    remarks = models.TextField()

class ProductsShare(models.Model):
    productname = models.CharField(max_length=30)
    pv = models.IntegerField()
    uv = models.IntegerField()
    date = models.CharField(max_length=10)
    datetype = models.CharField(max_length=2)
    itemname = models.CharField(max_length=30)
    platform = models.CharField(max_length=10)# ios/android/pc/web
    myType = models.CharField(max_length=10)# browser / os / dpi
    remarks = models.TextField()