# -*- coding:utf-8 -*-
import json
import os, tempfile, zipfile

import re
from bs4 import BeautifulSoup

from django.http import StreamingHttpResponse

from itest.settings import MEDIA_URL

from django.template import Context
import time
import requests
from django.shortcuts import render,render_to_response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.management.commands import flush
import datetime
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from requests import ConnectionError

from apiget.models import HoleInfo,TestInfos,FeedBack,MarketShare,ProductsShare
from itest.settings import BASE_DIR
LevelList = ["空","低","中","高","严重"]
StatusList = ["空","处理中","状态2","已修复","可接受风险","误报"]
ScanTypeList = ["空","漏洞跟踪","主机扫描","插件扫描"]
UpdateStatusList = ["没更新","状态2","处理中","已修复","可接受风险","误报"]

GroupLUNA = ["有道考研","有道手机版","有道专业翻译","有道网页翻译","有道四六级","有道词典","有道小组","有道口语大师",
             "有道翻译官","有道语文达人","有道英印词典","有道词典翻译论坛","有道词典FAQ"]
GroupYNOTE = ["有道云笔记","有道云笔记论坛",]
GroupEAD = ["有道搜索推广","有道E读","有道智选",]
GroupARMANI = ["惠惠网","惠惠购物助手","拼了App",]
GroupKE = ["有道精品课","有道学堂",]

GroupD = {'LUNA':GroupLUNA,'YNOTE':GroupYNOTE, 'EAD':GroupEAD, 'ARMANI':GroupARMANI, 'KE': GroupKE}
GroupOrder = ['LUNA', 'YNOTE', 'EAD', 'ARMANI','KE']

HOLEFILE = 'holeInfo'
TIMEFILE = 'uptime.txt'

#更新信息的服务器 在tb038x上使用 nohop python -m SimpleHTTPServer 23333 & 在后台永久挂起
_ResetUrl = 'http://tb038x.corp.youdao.com:23333/%s'


def _dblog(str):
    with open(BASE_DIR + '/log/changedb.log', 'a') as f:
        f.write(str + '\n')

#------------------------------------------------------holeinfo---------------------------------------------------------
#                                              安全部反馈的漏洞信息所用接口
#
#                            #     # ####### #       #######   ###   #     # ####### #######
#                            #     # #     # #       #          #    ##    # #       #     #
#                            #     # #     # #       #          #    # #   # #       #     #
#                            ####### #     # #       #####      #    #  #  # #####   #     #
#                            #     # #     # #       #          #    #   # # #       #     #
#                            #     # #     # #       #          #    #    ## #       #     #
#                            #     # ####### ####### #######   ###   #     # #       #######
#
#
#
#

#获取某个产品组的产品名单 用于表格查询的二级菜单
def ProductNameAPI(request):
    dbo = HoleInfo.objects
    if 'group' in request.GET:
        group = request.GET['group'].encode('utf-8')
        dret = {'name':[]}
        if group and group!='其他':
            namelist = GroupD[group]
            for item in namelist:
                dret['name'].append(item)
        else:
            if group=='其他':
                #排除其他组 不直接选择‘其他’组 防止错误
                for groupname in GroupD.keys():
                    dbo = dbo.exclude(groupName=groupname)
            namelist = dbo.values_list('productName').distinct()
            for item in namelist:
                dret['name'].append(item[0])
        dret['name'].sort(reverse=True)
        return JsonResponse(dret)

def GetVulTypeAPI(request):
    dbo = HoleInfo.objects
    ret = {}
    ret['vulType'] = list(dbo.values_list('vulType', flat=True).distinct())
    return JsonResponse(ret)

#获取表格数据
def HoleTableAPI(request):
    dbo = HoleInfo.objects
    dbo = _Selector(request, dbo)
    return JsonResponse(_TableJsonRp(dbo))

#获取统计数据
def StatisticsAPI(request):
    dbo = HoleInfo.objects
    dbo = _Selector(request, dbo)
    #统计模式
    if 'smode' in request.GET:
        smode = str(request.GET['smode'])
    else:
        smode = '0'
    #统计年数 选择出最新数据所在季度往前几年的所有季度
    if 'years' in request.GET:
        years = request.GET['years']
    else:
        years = 'all'
    if 'groupname' in request.GET:
        group = request.GET['groupname'].encode('utf-8')


    else:
        group = 'LUNA'
    ret = _StatisticsJsonRp(dbo, smode, years, group)
    return JsonResponse(ret)

#获取服务器数据 并且将json转为dict
def _HoleGet():
    #holeInfo 为远程数据文件 uptime.txt time.txt存储远程数据更新时间
    try:
        reqinfo = requests.get(_ResetUrl % HOLEFILE)
        reqtime = requests.get(_ResetUrl % TIMEFILE)
    except ConnectionError as e:
        return HttpResponse(e)

    timecontent = reqtime.content
    timefile = open('%s/time.txt' % BASE_DIR, 'wb')
    timefile.write(timecontent)
    timefile.close()

    infocontent = reqinfo.content
    drsp = json.loads(infocontent.decode('utf-8'))

    return drsp

#将一条漏洞信息写入数据库
def _HoleSave(hi):
    #可能存在targets不唯一的情况，暂且如此处理
    if not hi['targets']:
        targets = 'Null'
    else:
        targets = hi['targets']
    #分组
    group = '其他'
    productName = hi['productName'].encode('utf-8')
    if productName == '-':
        productName = targets

    for k in GroupD.keys():
        if productName in GroupD[k]:
            group = k
            break

    #方便筛选而构造季度字段
    hid = hi['id']
    quarter = hid[4:8]
    if int(hid[8:10]) < 4:
        quarter += 'Q1'
    elif int(hid[8:10]) < 7:
        quarter += 'Q2'
    elif int(hid[8:10]) < 10:
        quarter += 'Q3'
    else:
        quarter += 'Q4'

    HoleInfo(status=str(hi['status']),
             targetType=str(hi['targetType']),
             scanType=str(hi['scanType']),
             description=hi['description'],
             level=str(hi['level']),
             createTime=hi['createTime'],
             checkResult=hi['checkResult'],
             updateStatus=str(hi['updateStatus']),
             productName=productName,
             vulType = hi['vulType'],
             groupName=group,
             h_id=hi['id'],
             targets=targets,
             title =hi['title'],
             quarter=quarter).save()

#重置整个数据库 时间长 约半分钟
def HolesResetAPI(request):
    _HoleDelete()

    jtest = _HoleGet()

    for hi in jtest['holeInfos']:
        _HoleSave(hi)
    _dblog('Reset holeinfo at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return HttpResponse('ok')

#更新数据库 时间短
def HolesUpdateAPI(request):

    jtest = _HoleGet()

    dbo = HoleInfo.objects
    count = 0

    for hi in jtest['holeInfos']:
        touch = dbo.filter(h_id = hi['id'])
        if touch:
            if touch[0].createTime != hi['createTime']:
                _HoleSave(hi)
            else:
                continue
        else:
            _HoleSave(hi)
        count += 1
    _dblog('Update holeinfo at %s. Update %d entries.' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count))

    return HttpResponse(count)

#清空数据库数据
def _HoleDelete():
    HoleInfo.objects.all().delete()
    return 'ok'

#组装返回给表格的数据
def _TableJsonRp(dbos):
    jsonRes = {}
    for hi in dbos.all():
        jhi = dict()
        jhi['id'] = hi.h_id
        jhi['status'] = StatusList[int(hi.status)]
        jhi['productName'] = hi.productName
        jhi['targetType'] = hi.targetType
        jhi['level'] = LevelList[int(hi.level)]
        jhi['targets'] = hi.targets
        jhi['vulType'] = hi.vulType
        timeStamp = hi.createTime / 1000 + 8*60*60 #时区补正
        dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
        otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
        jhi['createTime'] = otherStyleTime
        jsonRes[hi.h_id] = jhi
    return jsonRes

#组装返回给统计图的数据
def _StatisticsJsonRp(dbos, smode, years, group):
    jsonRes = {'data':[] , 'xAxis': []}
    quartlist = dbos.values_list('quarter').distinct()

    if years != 'all':
        quartlist = quartlist[:int(years)*4]

    for quart in quartlist:
        jsonRes['xAxis'].append(quart[0])
    jsonRes['xAxis'].reverse()

    if smode == '1' :
        namelist = GroupOrder
        for item in namelist:
            productit = []
            for quarter in jsonRes['xAxis']:
                c = dbos.filter(groupName = item, quarter = quarter).count()
                productit.append(c)
            jsonRes['data'].append({"name": item, "value": productit})
        allit = []
        for quarter in jsonRes['xAxis']:
            c = dbos.filter(quarter=quarter).count()
            allit.append(c)
        jsonRes['data'].append({"name": '全部', "value": allit})


    elif smode == '2':
        namelist = GroupD[group]
        for item in namelist:
            productit = []
            for quarter in jsonRes['xAxis']:
                c = dbos.filter(productName = item, quarter = quarter).count()
                productit.append(c)
            jsonRes['data'].append({"name": item, "value": productit})
        allit = []
        for quarter in jsonRes['xAxis']:
            c = dbos.filter(quarter=quarter, groupName=group).count()
            allit.append(c)
        jsonRes['data'].append({"name": '全部', "value": allit})

    return jsonRes

#获取漏洞信息详情
def HoleDetailAPI(request):
    dbo = HoleInfo.objects
    if 'id' in request.GET:
        id = request.GET['id']
        if id:
            need = dbo.get(h_id=id)
            content = need.description
            title = need.title
            return JsonResponse({'content':content,'title':title})
        return  HttpResponse('id is null')
    else:
        return HttpResponse('no id')

#链式选择器
def _Selector(request, dbos):
    if 'targetType' in request.GET:
        targetType = request.GET['targetType']
        if targetType:
            dbos = dbos.filter(targetType=targetType)

    if 'level' in request.GET:
        level = str(request.GET['level'])
        if level:
            dbos = dbos.filter(level=level)

    if 'productName' in request.GET:
        productName = request.GET['productName']
        if productName:
            dbos = dbos.filter(productName = productName)

    if 'group' in request.GET:
        group = request.GET['group']
        if group:
            dbos = dbos.filter(groupName = group)


    if 'scanType' in request.GET:
        scanType = str(request.GET['scanType'])
        if scanType:
            dbos = dbos.filter(scanType=scanType)
    if 'status' in request.GET:
        status = str(request.GET['status'])
        if status:
            dbos = dbos.filter(status=status)
    if 'vulType' in request.GET:
        vulType = request.GET['vulType']
        if vulType:
            dbos = dbos.filter(vulType=vulType)
    #东八区的时间组出的时间戳实际多了八个小时 需要补正
    if 'bgdate' in request.GET:
        bgdate = request.GET['bgdate']
        if bgdate and bgdate != '':
            bgdate_date = datetime.datetime.strptime(bgdate,"%Y-%m-%d")
            timestamp = (time.mktime(bgdate_date.timetuple()))*1000 - 8*3600
            dbos = dbos.filter(createTime__gte = timestamp)
    if 'eddate' in request.GET:
        eddate = request.GET['eddate']
        if eddate and eddate != '':
            eddate += " 23:59:59"
            eddate_date = datetime.datetime.strptime(eddate,"%Y-%m-%d  %H:%M:%S")
            timestamp = (time.mktime(eddate_date.timetuple()))*1000 - 8*3600
            dbos = dbos.filter(createTime__lte = timestamp)
    if 'quarter' in request.GET:
        quarter = 'Q'+str(request.GET['quarter'])
        if quarter:
            dbos = dbos.filter(quarter__contains = quarter)
    if 'year' in request.GET:
        year = str(request.GET['year'])
        if year:
            dbos = dbos.filter(quarter__contains = year)
    return dbos






#-----------------------------------------------testinfo----------------------------------------------------------------
#                                      测试组季度信息review系统
#
#                    ####### #######  #####  #######   ###   #     # ####### #######
#                       #    #       #     #    #       #    ##    # #       #     #
#                       #    #       #          #       #    # #   # #       #     #
#                       #    #####    #####     #       #    #  #  # #####   #     #
#                       #    #             #    #       #    #   # # #       #     #
#                       #    #       #     #    #       #    #    ## #       #     #
#                       #    #######  #####     #      ###   #     # #       #######
#
#




#以产品组为单位统计--分产品数据
def ProductBugsAPI(request):
    dbo = TestInfos.objects.all()
    if 'name' in request.GET:
        name = request.GET['name']
    else:
        name = 'LUNA'
    qd = _QuarterD()
    dbo = dbo.filter(group=name, quarter__lte = qd['last'])

    if 'mode' in request.GET:
        mode = request.GET['mode']
    else:
        mode = '0'
    title = 'default title'
    myType = 'line'
    xAxis = []
    data = {}
    ret = {}
    #分产品分时段
    if mode == '1':
        if 'quarter' in request.GET:
            quarter = request.GET['quarter']
            if quarter:
                dbo = dbo.get(quarter=quarter)
                entry = dbo
                ret = {'发现BUG数':entry.bugs_found,'发现P1BUG数':entry.bugs_found_p1,'逃逸BUG数':entry.bugs_escape,
                       "逃逸P1BUG数":entry.bugs_escape_p1, "测试无责数": entry.bugs_escape_noduty}
            title_mode = '测试数据一览'.decode('utf-8')
            title = quarter+name+title_mode
            xAxis = ret.keys()
            xAxis.sort()
            d = []
            for xi in xAxis:
                d.append(ret[xi])
            data = {'BUG数':d}
            myType = 'bar'

    #分产品分类别
    if mode == '2':
        if 'case' in request.GET:
            case = request.GET['case']
        else:
            case = '0'

        def pmode2f(count):
            if count!='':
                ret[entry.quarter[2:]] = int(count)

        title_mode1 = '数据详情'.decode('utf-8')
        title_mode2 = ['发现BUG数','发现P1BUG数','逃逸BUG数','逃逸P1BUG数','准入测试次数','通过准入测试次数',
                       '功能发现BUG数','功能发现P1BUG数','性能发现BUG数','性能发现P1BUG数']

        tm2 = []
        for t in title_mode2:
            tm2.append(t.decode('utf-8'))
        title_mode2 = tm2

        title = title_mode2[int(case)-1]+title_mode1

        if case == '1':
            for entry in dbo:
                pmode2f(entry.bugs_found)
        elif case == '2':
            for entry in dbo:
                pmode2f(entry.bugs_found_p1)
        elif case == '3':
            for entry in dbo:
                pmode2f(entry.bugs_escape)
        elif case == '4':
            for entry in dbo:
                pmode2f(entry.bugs_escape_p1)
        elif case == '5':
            for entry in dbo:
                pmode2f(entry.allow_tests)
        elif case == '6':
            for entry in dbo:
                pmode2f(entry.allow_tests_pass)
        elif case == '7':
            for entry in dbo:
                pmode2f(entry.bugs_found_function)
        elif case == '8':
            for entry in dbo:
                pmode2f(entry.bugs_found_function_p1)
        elif case == '9':
            for entry in dbo:
                pmode2f(entry.bugs_other)
        elif case == '10':
            for entry in dbo:
                pmode2f(entry.bugs_other_p1)

        q = ret.keys()
        q.sort()
        d = []
        for qi in q:
            d.append(ret[qi])
        data = {'BUG数': d}
        xAxis = q

    ret = {'xAxis': xAxis, 'data': data, 'type': myType, 'title': title}
    return JsonResponse(ret)

#分季度数据--本季度业务成果
def QuartersBugsAPI(request):
    dbo = TestInfos.objects.all()
    if 'mode' in request.GET:
        mode = request.GET['mode']
    else:
        mode = '0'
    if 'case' in request.GET:
        case = request.GET['case']
    else:
        case = '0'
    if 'quarters' in request.GET:
        quarters = request.GET['quarters']
        if quarters and quarters!='0':
            qd = _QuarterD()
            dbo = dbo.filter(quarter__lte = qd['last']).order_by('-quarter')
            firstquarter = list(dbo.values_list('quarter', flat=True).distinct().order_by('-quarter'))[int(quarters)-1]
            dbo = dbo.filter(quarter__gte=firstquarter).order_by('-quarter')

    title = 'default title'
    myType = 'line'
    xAxis = []
    data = {}
    ret = {}
    #发现bug数
    if mode == '1':
        def mode1f(bugs_found):
            count = bugs_found
            if not count:
                count = 0
            if ret.has_key(entry.quarter[2:]):
                ret[entry.quarter[2:]] += int(count)
            else:
                ret[entry.quarter[2:]] = int(count)
        if case == '1':
            title = '发现BUG数'
            for entry in dbo:
                mode1f(entry.bugs_found)
        elif case == '2':
            title = '发现P1BUG数'
            for entry in dbo:
                mode1f(entry.bugs_found_p1)
        q = ret.keys()
        q.sort()
        bc = []
        for qu in q:
            bc.append(ret[qu])
        xAxis = q
        data = {'发现BUG个数': bc}

    #逃逸bug数
    elif mode == '2':

        def mode2f(bugs_escape,bugs_escape_noduty):
            count = bugs_escape
            count_noduty = bugs_escape_noduty
            if not count:
                count = 0
            if not count_noduty:
                count_noduty = 0
            if ret.has_key(entry.quarter[2:]):
                ret[entry.quarter[2:]]['escapes'] += int(count)
                ret[entry.quarter[2:]]['noduty'] += int(count_noduty)
            else:
                ret[entry.quarter[2:]] = {'escapes': int(count), 'noduty': int(count_noduty)}

        if case == '1':
            title = '逃逸BUG数'
            for entry in dbo:
                mode2f(entry.bugs_escape, entry.bugs_escape_noduty)
        elif case == '2':
            title = '逃逸P1BUG数'
            for entry in dbo:
                mode2f(entry.bugs_escape_p1, entry.bugs_escape_p1_noduty)

        q = ret.keys()
        q.sort()
        ec = []
        dc = []
        for qu in q:
            ec.append(ret[qu]['escapes'])
            dc.append(int(ret[qu]['escapes']-ret[qu]['noduty']))
        xAxis = q
        data = {'线上所有故障':ec, '测试主要责任': dc}

    #逃逸率
    elif mode == '3':
        if case == '1':
            title = '逃逸率'
            for entry in dbo:
                if entry.bugs_escape == '':
                    count_escape = 0
                else:
                    count_escape = int(entry.bugs_escape)
                if entry.bugs_found == '':
                    count = count_escape
                else:
                    count = int(entry.bugs_found) + int(entry.bugs_escape)
                if entry.bugs_escape_noduty == '':
                    count_noduty = 0
                else:
                    count_noduty = int(entry.bugs_escape_noduty)

                if ret.has_key(entry.quarter[2:]):
                    ret[entry.quarter[2:]]['count'] += int(count)
                    ret[entry.quarter[2:]]['escapes'] += int(count_escape)
                    ret[entry.quarter[2:]]['noduty'] += int(count_noduty)
                else:
                    ret[entry.quarter[2:]] = {'count': int(count), 'escapes': int(count_escape), 'noduty': int(count_noduty)}
        q = ret.keys()
        q.sort()
        er = []
        dr = []
        for qu in q:
            er.append("%.2f" % (float(100*ret[qu]['escapes'])/ret[qu]['count']))
            dr.append("%.2f" % (float(100*(ret[qu]['escapes']-ret[qu]['noduty']))/ret[qu]['count']))
        xAxis = q
        data = {'线上所有故障': er, '测试主要责任': dr}

    #各产品发现bug数
    elif mode == '4':
        def mode4f(bugscount):
            if bugscount == '':
                count = 0
            else:
                count = bugscount
            if ret.has_key(entry.group):
                if ret[entry.group].has_key(entry.quarter[2:]):
                    pass
                else:
                    ret[entry.group][entry.quarter[2:]] = count
            else:
                ret[entry.group] = {entry.quarter[2:]: count}
        if case == '1':
            title = '各产品发现BUG总数'
            for entry in dbo:
                mode4f(entry.bugs_found)
        elif case == '2':
            title = '各产品发现P1BUG数'
            for entry in dbo:
                mode4f(entry.bugs_found_p1)
        elif case == '3':
            title = '各产品逃逸BUG数'
            for entry in dbo:
                mode4f(entry.bugs_escape)
        x = GroupOrder
        dp = {}
        for qu in x:
            for k in ret[qu].keys():
               if dp.has_key(k):
                   dp[k].append(ret[qu][k])
               else:
                   dp[k] = [ret[qu][k],]
        xAxis = x
        data = dp
        myType = 'bar'

    ret = {'xAxis': xAxis,'data':data, 'title': title, 'type': myType}
    return JsonResponse(ret)

#获取存在的季度
def GetQuartersAPI(request):
    dbo = TestInfos.objects
    qlist = dbo.values_list('quarter').distinct()
    dret = {'quarters': []}
    if 'need' in request.GET:
        need = request.GET['need']
    for item in qlist:
        qd = _QuarterD()
        if item[0] <= qd[need]:
            dret['quarters'].append(item[0])
    dret['quarters'].sort(reverse=True)
    dret['qd'] = qd
    return JsonResponse(dret)

#获取按序号的组名
def GetOrderGroupsAPI(request):
    return JsonResponse({'ordergroup':GroupOrder})
#反馈信息
def FeedBackAPI(request):
    dbo = FeedBack.objects.all()
    title = 'default title'
    myType = 'line'
    xAxis = []
    data = {}
    other = {}
    ret = {}

    if 'mode' in request.GET:
        mode = request.GET['mode']
        if mode == '1':
            title = '测试组质量与效率评分'
            ret = {'gradec':{},}
            for entry in dbo:
                if ret['gradec'].has_key(entry.date[2:6]):
                    ret['gradec'][entry.date[2:6]]['count'] += 1
                    ret['gradec'][entry.date[2:6]]['grade1'] += entry.grade1
                    ret['gradec'][entry.date[2:6]]['grade2'] += entry.grade2
                else:
                    ret['gradec'][entry.date[2:6]] = {'count':1, 'grade1':entry.grade1, 'grade2': entry.grade2}

            q = ret['gradec'].keys()
            q.sort()
            g1l = []
            g2l = []
            for qu in q:
                c = ret['gradec'][qu]['count']
                if c:
                    g1l.append('%.2f' % (float(ret['gradec'][qu]['grade1']) / c))
                    g2l.append('%.2f' % (float(ret['gradec'][qu]['grade2']) / c))
                else:
                    g1l.append('0')
                    g2l.append('0')
            ret['gradec'] = {'测试质量平均分': g1l, '测试效率平均分': g2l}
            xAxis = q
            data = ret['gradec']

        elif mode == '2':
            title = '第三方反馈问题分类'
            ret = {"缺少机器":0,"缺少人力":0,"BUG质量相关":0,"建议其他":0,"单纯夸赞":0,
                   "测试流程相关":0,"沟通相关":0,"逃逸相关":0,"无意见提交":0,}
            for entry in dbo:
                flag = 0
                if entry.need_machine == 'Y':
                    ret["缺少机器"] += 1
                    flag = 1
                if entry.need_person == 'Y':
                    ret["缺少人力"] += 1
                    flag = 1
                if entry.bug_qua == 'Y':
                    ret["BUG质量相关"] += 1
                    flag = 1
                if entry.suggest == 'Y':
                    ret["建议其他"] += 1
                    flag = 1
                if entry.good == 'Y':
                    ret["单纯夸赞"] += 1
                    flag = 1
                if entry.process == 'Y':
                    ret["测试流程相关"] += 1
                    flag = 1
                if entry.chat == 'Y':
                    ret["沟通相关"] += 1
                    flag = 1
                if entry.escape1 == 'Y':
                    ret["逃逸相关"] += 1
                    flag = 1
                if flag == 0:
                    ret["无意见提交"] += 1
            x = ret.keys()
            x.sort()
            dl = []
            for xi in x:
                dl.append(ret[xi])
            xAxis = x
            data = {"数量": dl}
            myType = 'bar'

        elif mode == '3':
            ret['list'] = []
            dbo = dbo.exclude(feedback_done='Y')
            for entry in  dbo:
                ret['list'].append({'name': entry.name,'content': entry.feedback})
            return JsonResponse(ret)

        elif mode == '4':
            for entry in dbo:
                if ret.has_key(entry.name):
                    ret[entry.name] += 1
                else:
                    ret[entry.name] = 1
            return JsonResponse(ret)

        elif mode == '0':
            ret = {'groupc':{}, 'donec': 0, 'ndonec': 0}
            for entry in dbo:
                if ret['groupc'].has_key(entry.group):
                    ret['groupc'][entry.group] += 1
                else:
                    ret['groupc'][entry.group] = 1
                if entry.feedback_done == 'Y':
                    ret['donec'] += 1
                else:
                    ret['ndonec'] += 1
            return JsonResponse(ret)
    ret = {'xAxis': xAxis, 'data': data, 'type': myType, 'title': title, 'other': other}
    return JsonResponse(ret)

#上传反馈数据
@csrf_exempt
def FBUploadAPI(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        group = request.POST.get('group')
        name = request.POST.get('name')
        grade1 = float(request.POST.get('grade1'))
        grade2 = float(request.POST.get('grade2'))
        if 'need_machine' in request.POST and request.POST.get('need_machine') == 'Y':
            need_machine = 'Y'
        else:
            need_machine = ''
        if 'need_person' in request.POST and request.POST.get('need_person') == 'Y':
            need_person = 'Y'
        else:
            need_person = ''
        if 'bug_qua' in request.POST and request.POST.get('bug_qua') == 'Y':
            bug_qua = 'Y'
        else:
            bug_qua = ''
        if 'suggest' in request.POST and request.POST.get('suggest') == 'Y':
            suggest = 'Y'
        else:
            suggest = ''
        if 'good' in request.POST and request.POST.get('good') == 'Y':
            good = 'Y'
        else:
            good = ''
        if 'process' in request.POST and request.POST.get('process') == 'Y':
            process = 'Y'
        else:
            process = ''
        if 'chat' in request.POST and request.POST.get('chat') == 'Y':
            chat = 'Y'
        else:
            chat = ''
        if 'escape1' in request.POST and request.POST.get('escape1') == 'Y':
            escape1 = 'Y'
        else:
            escape1 = ''
        if 'feedback' in request.POST:
            feedback = request.POST.get('feedback')
        else:
            feedback = ''
        FeedBack(date = date, name = name, group = group, grade1 = grade1, grade2 = grade2,
                 need_machine = need_machine, need_person = need_person, bug_qua = bug_qua,
                 suggest = suggest, good = good, process = process, chat = chat, escape1 = escape1,
                 feedback = feedback, feedback_done = 'Y').save()

        _dblog('Edit feedback at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return HttpResponseRedirect('/fbupload')
            
#上传季度数据
@csrf_exempt
def TIUpdate(request):
    if request.method == 'POST':
        dbo = TestInfos.objects
        group = request.POST.get('group')
        quarter = request.POST.get('quarter')
        matchcase = dbo.filter(group = group, quarter = quarter)
        #已存在，更新
        if len(matchcase) == 1:
            matchcase.update(bugs_found=request.POST.get('found'), bugs_found_p1=request.POST.get('found_p1'),
                                bugs_escape=request.POST.get('escape'), bugs_escape_p1=request.POST.get('escape_p1'),
                                bugs_escape_noduty=request.POST.get('escape_noduty'),
                                bugs_escape_p1_noduty=request.POST.get('escape_p1_noduty'),
                                bugs_escape_info=request.POST.get('escape_info'),
                                bugs_found_function=request.POST.get('found_function'),
                                bugs_found_function_p1=request.POST.get('found_function_p1'),
                                bugs_other=request.POST.get('other'), bugs_other_p1=request.POST.get('other_p1'),
                                allow_tests=request.POST.get('allow_tests'),
                                allow_tests_pass=request.POST.get('allow_tests_pass'))
            _dblog('Update testinfo at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        #不存在，创建
        elif len(matchcase) == 0:
            t_id = quarter[:4] + quarter[-1]
            if group == 'LUNA':
                t_id += '1'
            elif group == 'YNOTE':
                t_id += '2'
            elif group == 'EAD':
                t_id += '3'
            elif group == 'ARMANI':
                t_id += '4'
            elif group == 'KE':
                t_id += '5'
            else:
                t_id += '0'
            TestInfos(group = group, quarter = quarter,
                      bugs_found=request.POST.get('found'), bugs_found_p1=request.POST.get('found_p1'),
                                bugs_escape=request.POST.get('escape'), bugs_escape_p1=request.POST.get('escape_p1'),
                                bugs_escape_noduty=request.POST.get('escape_noduty'),
                                bugs_escape_p1_noduty=request.POST.get('escape_p1_noduty'),
                                bugs_escape_info=request.POST.get('escape_info'),
                                bugs_found_function=request.POST.get('found_function'),
                                bugs_found_function_p1=request.POST.get('found_function_p1'),
                                bugs_other=request.POST.get('other'), bugs_other_p1=request.POST.get('other_p1'),
                                allow_tests=request.POST.get('allow_tests'),
                                allow_tests_pass=request.POST.get('allow_tests_pass'),t_id = t_id).save()
            _dblog('New testinfo at ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return HttpResponseRedirect('/update')

#获取季度信息
def GetLastEntryAPI(request):
    dbo = TestInfos.objects
    if 'quarter' in request.GET:
        quarter = request.GET['quarter']
    else:
        quarter = ''
    if 'group' in request.GET:
        group = request.GET['group']
    else:
        group = 'LUNA'

    lastentry = dbo.get(group = group, quarter = quarter)

    ret = {'quarter': lastentry.quarter, 'group': lastentry.group, 'found': lastentry.bugs_found,
           'found_p1': lastentry.bugs_found_p1,'escape': lastentry.bugs_escape,'escape_p1': lastentry.bugs_escape_p1,
           'escape_noduty': lastentry.bugs_escape_noduty,'escape_p1_noduty': lastentry.bugs_escape_p1_noduty,
           'escape_info': lastentry.bugs_escape_info,'found_function': lastentry.bugs_found_function,
           'found_function_p1': lastentry.bugs_found_function_p1,'other': lastentry.bugs_other,
           'other_p1': lastentry.bugs_other_p1,'allow_tests': lastentry.allow_tests,
           'allow_tests_pass': lastentry.allow_tests_pass,}
    return JsonResponse(ret)

def _QuarterD():
    nowtime = datetime.datetime.now()
    nowquarter = str(nowtime.year)
    if int(nowtime.month) < 4:
        lastquarter = str(int(nowquarter) - 1) + 'Q4'
        nowquarter += 'Q1'
    elif int(nowtime.month) < 7:
        lastquarter = nowquarter + 'Q1'
        nowquarter += 'Q2'
    elif int(nowtime.month) < 10:
        lastquarter = nowquarter + 'Q2'
        nowquarter += 'Q3'
    else:
        lastquarter = nowquarter + 'Q3'
        nowquarter += 'Q4'
    return {'new': nowquarter, 'last': lastquarter}

#获取文件名
def GetFileNameAPI(request):
    filelist = os.listdir("%s/%sexcel" % (BASE_DIR, MEDIA_URL,))
    return JsonResponse({"filelist": filelist,})

#下载文件
def FileDownloadAPI(request):
    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    if 'filename' in request.GET:
        filename = request.GET['filename']
        the_file_name = "%s/%sexcel/%s" % (BASE_DIR, MEDIA_URL, filename)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)
        return response

# ------------------------------------------------------markshare-------------------------------------------------------
#                                              来自各大统计网站的市场份额信息
#
#
#                                        #    #    ##    #####   #    #  ######   #####
#                                        ##  ##   #  #   #    #  #   #   #          #
#                                        # ## #  #    #  #    #  ####    #####      #
#                                        #    #  ######  #####   #  #    #          #
#                                        #    #  #    #  #   #   #   #   #          #
#                                        #    #  #    #  #    #  #    #  ######     #
#
#                                             ####   #    #    ##    #####   ######
#                                            #       #    #   #  #   #    #  #
#                                             ####   ######  #    #  #    #  #####
#                                                 #  #    #  ######  #####   #
#                                            #    #  #    #  #    #  #  #    #
#                                             ####   #    #  #    #  #    #  ######

#获取市场份额信息数据
def GetMarketShareAPI(request):
    dbo = MarketShare.objects
    if 'platform' in request.GET:
        platform = request.GET['platform']
        if platform:
            dbo = dbo.filter(platform = platform)
    if 'type' in request.GET:
        myType = request.GET['type']
        if myType:
            dbo = dbo.filter(myType = myType)
    if 'market' in request.GET:
        market = request.GET['market']
        if market:
            dbo = dbo.filter(market = market)
    if 'months' in request.GET:
        months = int(request.GET['months'])
    ret = {}
    sitelist = list(dbo.values_list('sourcename',flat=True).distinct())

    for site in sitelist:
        needdbo = dbo.filter(sourcename=site)
        datelist = list(needdbo.values_list('date', flat=True).distinct().order_by('date'))
        ret[site] = {'data':{},'src': needdbo.all()[0].source, 'remarks': needdbo.all()[0].remarks}
        if (months <= len(datelist)):
            needdbo = needdbo.filter(date__gte = datelist[-months]).order_by('date')
            ret[site]['date'] = datelist[-months:]
        else:
            ret[site]['date'] = datelist

        namelist = list(set(needdbo.values_list('itemname', flat=True)))
        for date in ret[site]['date']:
            for itemname in namelist:
                touch = needdbo.filter(itemname = itemname, date=date)
                if touch.count() != 0:
                    if ret[site]['data'].has_key(itemname):
                        ret[site]['data'][itemname]['value'].append(touch[0].value)
                    else:
                        ret[site]['data'][itemname] = {'value':[touch[0].value,]}
                else:
                    if ret[site]['data'].has_key(itemname):
                        ret[site]['data'][itemname]['value'].append(0)
                    else:
                        ret[site]['data'][itemname] = {'value':[0,]}

    return JsonResponse(ret)


# ------------------------------------------------------productsshare-------------------------------------------------------
#                                             来自李斯宁的公司各产品的用户数据信息
#
#
#
#                                             ####   #    #    ##    #####   ######
#                                            #       #    #   #  #   #    #  #
#                                             ####   ######  #    #  #    #  #####
#                                                 #  #    #  ######  #####   #
#                                            #    #  #    #  #    #  #  #    #
#                                             ####   #    #  #    #  #    #  ######
def GetProductShareAPI(request):
    dbo = ProductsShare.objects
    platform = myType = productname = datetype = ''
    if 'platform' in request.GET:
        platform = request.GET['platform']
        if platform:
            dbo = dbo.filter(platform = platform)
    if 'type' in request.GET:
        myType = request.GET['type']
        if myType:
            dbo = dbo.filter(myType = myType)
    if 'productname' in request.GET:
        productname = request.GET['productname']
        if productname:
            dbo = dbo.filter(productname = productname)
    if 'datetype' in request.GET:
        datetype = request.GET['datetype']
        if datetype in ['D', 'M', 'W']:
            dbo = dbo.filter(datetype = datetype)
    if 'mode' in request.GET:
        mode = request.GET['mode']
    else:
        mode = '1'
    datelist = list(dbo.values_list('date', flat=True).distinct().order_by('date'))
    ret = {'result':{'pv': {'data':{}}, 'uv': {'data':{}}}, 'title': '', 'date':[]}

    if mode == '1':
        ret['title'] = '%s - %s - %s - %s' % (datelist[-1], dbo[0].productname, dbo[0].platform, dbo[0].myType)
        dbo = dbo.filter(date = datelist[-1])
        ret['date'] = datelist[-1]
        for o in dbo:
            ret['result']['pv']['data'][o.itemname] = {'value':o.pv}
            ret['result']['uv']['data'][o.itemname] = {'value': o.uv}
    elif mode == '2':
        dates = []
        if datetype == 'D':
            if len(datelist) > 30:
                dates = datelist[-30:]
            else:
                dates = datelist
        elif datetype == 'W':
            weeklist = datelist[::7]
            if len(weeklist) > 12:
                dates = weeklist[-12:]
            else:
                dates = weeklist
        elif datetype == 'M':
            monthlist = datelist[::30]
            if len(monthlist) > 12:
                dates = monthlist[-12:]
            else:
                dates = monthlist
        ret['title'] = '%s ~ %s - %s - %s - %s' % (dates[0], dates[-1], productname, platform, myType)
        ret['date'] = dates
        namelist = list(dbo.values_list('itemname', flat=True).distinct())
        for itemname in namelist:
            for date in dates:
                touch = dbo.filter(date = date, itemname = itemname)
                if touch.count() != 0:
                    if ret['result']['pv']['data'].has_key(itemname):
                        ret['result']['pv']['data'][itemname]['value'].append(touch[0].pv)
                        ret['result']['uv']['data'][itemname]['value'].append(touch[0].uv)
                    else:
                        ret['result']['pv']['data'][itemname] = {'value': [touch[0].pv, ]}
                        ret['result']['uv']['data'][itemname] = {'value': [touch[0].uv, ]}
                else:
                    if ret['result']['pv']['data'].has_key(itemname):
                        ret['result']['pv']['data'][itemname]['value'].append(0)
                        ret['result']['uv']['data'][itemname]['value'].append(0)
                    else:
                        ret['result']['pv']['data'][itemname] = {'value': [0, ]}
                        ret['result']['uv']['data'][itemname] = {'value': [0, ]}
    return JsonResponse(ret)

def GetPSFormItem(request):
    dbo = ProductsShare.objects
    productname = list(dbo.values_list('productname', flat=True).distinct())
    myType = list(dbo.values_list('myType', flat=True).distinct())
    platform = list(dbo.values_list('platform', flat=True).distinct())
    return JsonResponse({'productname': productname, 'type': myType, 'platform': platform})


