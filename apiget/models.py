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
    h_id = models.CharField(max_length=20)
    targets = models.TextField()
