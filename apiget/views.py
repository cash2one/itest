# -*- coding:utf-8 -*-
import json
import time
from django.shortcuts import render,render_to_response
from django.utils import timezone
from django.core.management.commands import flush
import datetime
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from apiget.models import information,HoleInfo
LevelList = ["空","低","中","高","严重"]
StatusList = ["空","处理中","状态2","已修复","可接受风险","误报"]
ScanTypeList = ["空","漏洞跟踪","主机扫描","插件扫描"]
UpdateStatusList = ["没更新","状态2","处理中","已修复","可接受风险","误报"]

# status = models.CharField(max_length=2)
#     targetType = models.CharField(max_length=10)
#     scanType = models.CharField(max_length=2)
#     description = models.TextField()
#     level = models.CharField(max_length=2)
#     createTime = models.BigIntegerField()
#     checkResult = models.BooleanField()
#     updateStatus = models.CharField(max_length=2)
#     productName = models.CharField(max_length=50)
#     id = models.CharField(max_length=20)
#     targets = models.TextField()
#     offset = models.IntegerField
def home(request):
    return render(request, 'index.html')

def ProducnNameAPI(request):
    dbo = HoleInfo.objects
    ret = dbo.values_list('productName').distinct()
    d = dict()
    for item in ret:
        d[item[0]]={"name":item[0]}
    return JsonResponse(d)

def HolesResetAPI(request):
    # if  HoleInfo.objects.all():
    #     entry = HoleInfo.objects.all()
    #     HoleDelete()
    #     wfile = open('/home/ckthewu/djangoproject/itest/%s.json' % timezone.now(),'w')
    #     wfile.write(entry)
    #     wfile.close()
    HoleDelete()
    file = open('/home/ckthewu/djangoproject/itest/holeInfo','r')
    test = file.read()
    jtest = json.loads(test)
    for hi in jtest['holeInfos']:
        if not hi['targets']:
            targets = 'Null'
        else:
            targets = ','.join(hi['targets'])
        HoleInfo(status = str(hi['status']),
                 targetType = str(hi['targetType']),
                 scanType = str(hi['scanType']),
                 description = hi['description'],
                 level = str(hi['level']),
                 createTime = hi['createTime'],
                 checkResult = hi['checkResult'],
                 updateStatus = str(hi['updateStatus']),
                 productName = hi['productName'],
                 h_id = hi['id'],
                 targets = targets).save()
    return HttpResponse('ok')

def HoleDelete():
    HoleInfo.objects.all().delete()
    return 'ok'

def HoleGetAPI(request):
    dbo = HoleInfo.objects
    dbo = dbo.order_by('createTime').reverse()[:50]
    return JsonResponse(JsonRp(dbo.all()))

def JsonRp(objl):
    jsonRes = {}
    for hi in objl:
        jhi = dict()
        jhi['id'] = hi.h_id
        jhi['status'] = StatusList[int(hi.status)]
        jhi['productName'] = hi.productName
        jhi['targetType'] = hi.targetType
        jhi['level'] = LevelList[int(hi.level)]
        jhi['updateStatus'] = UpdateStatusList[int(hi.updateStatus)]
        jhi['targets'] = hi.targets
        timeStamp = hi.createTime / 1000 + 8*60*60 #change utc to utc+8
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        jhi['createTime'] = otherStyleTime
        jsonRes[hi.h_id] = jhi
    return jsonRes




def HoleDetailAPI(request):
    dbo = HoleInfo.objects
    if 'id' in request.GET:
        id = request.GET['id']
        if id:
            content = dbo.get(h_id=id).description
            return render_to_response('detail.html',{'content':content},request)
        return  HttpResponse('id is null')
    else:
        return HttpResponse('no id')

def HoleSelectAPI(request):
    dbo = HoleInfo.objects
    ret = []
    # if 'status' in request.GET:
    #     status = request.GET['status']
    #     for item in dbo.filter(status=status):
    #         ret.append(item.h_id)
    #     return HttpResponse(','.join(ret))
    # if 'time' in request.GET:
    #     time = int(request.GET['time'])
    #     for item in dbo.all():
    #         if item.createTime>time:
    #             ret.append(item.h_id)
    #     return HttpResponse(','.join(ret))
    if 'targetType' in request.GET:
        targetType = request.GET['targetType']
        if targetType:
            dbo = dbo.filter(targetType=targetType)
    if 'level' in request.GET:
        level = str(request.GET['level'])
        if level:
            dbo = dbo.filter(level=level)
    if 'productName' in request.GET:
        productName = request.GET['productName']
        if productName:
            dbo = dbo.filter(productName=productName)
    if 'scanType' in request.GET:
        scanType = str(request.GET['scanType'])
        if scanType:
            dbo = dbo.filter(scanType=scanType)
    if 'status' in request.GET:
        status = str(request.GET['status'])
        if status:
            dbo = dbo.filter(status=status)
    if 'bgdate' in request.GET:
        bgdate = request.GET['bgdate']
        if bgdate:
            bgdate_date = datetime.datetime.strptime(bgdate,"%Y-%m-%d")
            timestamp = time.mktime(bgdate_date.timetuple())*1000
            dbo = dbo.filter(createTime__gt = timestamp)
    if 'eddate' in request.GET:
        eddate = request.GET['eddate']
        if eddate:
            eddate_date = datetime.datetime.strptime(eddate,"%Y-%m-%d")
            timestamp = time.mktime(eddate_date.timetuple())*1000
            dbo = dbo.filter(createTime__lt = timestamp)
    if 'quarter' in request.GET and 'year' in request.GET:
        quarter = str(request.GET['quarter'])
        year = str(request.GET['year'])
        if quarter and year:
            if quarter == '1':
                bg = "%s-01-01" % year
                ed = "%s-03-31" % year
            elif quarter == '2':
                bg = "%s-04-01" % year
                ed = "%s-06-30" % year
            elif quarter == '3':
                bg = "%s-07-01" % year
                ed = "%s-09-30" % year
            elif quarter == '4':
                bg = "%s-10-01" % year
                ed = "%s-12-31" % year
            else:
                bg = "%s-01-01" % year
                ed = "%s-12-31" % year
            bgdate_date = datetime.datetime.strptime(bg, "%Y-%m-%d")
            timestamp = time.mktime(bgdate_date.timetuple()) * 1000
            dbo = dbo.filter(createTime__gt=timestamp)

            eddate_date = datetime.datetime.strptime(ed, "%Y-%m-%d")
            timestamp = time.mktime(eddate_date.timetuple()) * 1000
            dbo = dbo.filter(createTime__lt=timestamp)
    return JsonResponse(JsonRp(dbo.order_by('-createTime').all()))



def apisearchview(request):
    for t in request.GET:
        Class = request.GET[t]
        content = []
        for i in information.objects.all():
            if i.Class==Class:
                content.append(i.Name)
        r = ','.join(content)
        return HttpResponse(r)
    return HttpResponseRedirect('/')