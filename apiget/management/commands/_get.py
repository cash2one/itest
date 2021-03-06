# coding:utf-8
import httplib
import json
import re
from bs4 import BeautifulSoup
import time
import requests
import datetime
from requests import ConnectionError
from requests.exceptions import Timeout
from itest.settings import BASE_DIR
from apiget.models import MarketShare,ProductsShare
#获取市场份额数据时的日志
def _getlog(str):
    with open('%s/log/getms.log' % BASE_DIR, 'a') as f:
        print str
        f.write(str + '\n')

#获取www.netmarketshare.com的数据，存入数据库
def getNetMarketShare():
    #提取时间信息的正则，用于计算月份数
    monthmode = re.compile(r'^(\d{4})-(\d{2})')


    #统一化存储时的月份结构
    def dateform(str):
        d = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07',
             'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',}
        year = str[-4:]
        month = d[str[:-6]]
        return year + '-' + month

    #计算月份数，以1999年1月为第0月。
    def monthcount(str):
        print str
        year, month = monthmode.match(str).groups()
        return (int(year) - 1999) * 12 + int(month) - 1

    #每次抓取最近一年的每月数据。qpsp 起始月份的月份数，qpnp 月份数量。
    now = datetime.datetime.now()
    bg = str(now.year - 1) + '-' + ('0'+str(now.month))[-2:]
    qpsp = monthcount(bg)
    qpnp = 12

    #第一次访问主页用于获取sessionid
    init = requests.get('http://netmarketshare.com/')
    cookies = {"ASP.NET_SessionId": "kx0f1rjn4a1h4askp4qogr0r",
               "ppu_main_124111d1af66eb0c050ddea0602fe67f": "1",
               "ppu_sub_124111d1af66eb0c050ddea0602fe67f": "2", "__support_check": "1",
               "__na_u_63653888": "27021642135076",
               "__na_c": "1", "__na_u_102463488": "60884244633757", "__na_u_94599168": "7047127001031"}

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"}
    cookies['ASP.NET_SessionId'] = init.cookies['ASP.NET_SessionId']

    #暂时不影响，一个自动id
    qpcid = ''

    #浏览器桌面 浏览器手机 操作系统按版本桌面 操作系统手机
    qpgroup = ((3, 0), (1, 1), (11, 0), (11, 1))
    count = skipcount = updatecount = errorcount = 0
    for (qprid, qpcustomd) in qpgroup:
        url = "http://netmarketshare.com/common/pages/reportexport?uimyType=dialog&" \
              "url=%%2freport.aspx%%3fqprid%%3d%s%%26qptimeframe%%3dM%%26qpsp%%3d%s%%26qpnp%%3d%s%%26qpch%%3d350%%26" \
              "qpdisplay%%3d111111111111110%%26qpdt%%3d1%%26qpct%%3d4%%26qpcustomb%%3d%s%%26qpcid%%3d%s%%26qpf%%3d13&exportpageloaded=1" \
              % (qprid, qpsp, qpnp, qpcustomd, qpcid)
        try:
            geturl = requests.get(url, headers=header, cookies=cookies)
        except ConnectionError as e:
            _getlog('Error:' + str(e) + ' in connet to' + url)
            continue

        if geturl.status_code == 200:
            infomation = geturl.text
            #该接口数据类型为xml
            soup = BeautifulSoup(infomation, "xml")
            if soup.select('dataset'):
                if qprid == 3:
                    platform, myType = 'desktop', 'browser'
                elif qprid == 1:
                    platform, myType = 'mobile', 'browser'
                elif qprid == 11:
                    if qpcustomd == 0:
                        platform, myType = 'desktop', 'os'
                    else:
                        platform, myType = 'mobile', 'os'
                else:
                    platform, myType = 'desktop', 'browser'


                d = soup.select('dataset')[0].children
                rd = {'data': {}, 'month': []}
                for item in d:
                    if (item.name):
                        #因为这个xml格式的问题，只能这样处理数据
                        #其中为row的标签存储的是名称，其他的是各月份数据
                        if (item.name != 'row'):
                            if item.name[-1] != '1':
                                rd['data'][item.name[-1]] = {'name': item.get_text(), 'value': []}
                        else:
                            for v in item:
                                if (v.name):
                                    if v.name[-1] == '1':
                                        rd['month'].append(dateform(v.get_text()))
                                    else:
                                        rd['data'][v.name[-1]]['value'].append(float(v.get_text()[:-1]))
                for k in rd['data'].keys():
                    i = 0
                    while i < len(rd['data'][k]['value']):
                        #判断是否新数据，是否需要更新或者跳过
                        touch = MarketShare.objects.filter(date=rd['month'][i], sourcename='netmarketshare',
                                                           platform=platform, myType=myType,
                                                           market='ww', itemname=rd['data'][k]['name'])
                        if touch:
                            if  touch[0].value != float(rd['data'][k]['value'][i]):
                                touch.update(value=float(rd['data'][k]['value'][i]))
                                count += 1
                                updatecount += 1
                                print 'update'
                            else:
                                skipcount += 1
                                print 'skip'
                        else:
                            MarketShare(date=rd['month'][i],
                                        source='http://netmarketshare.com/', sourcename='netmarketshare',
                                        platform=platform, myType=myType,
                                        market='ww', value=float(rd['data'][k]['value'][i]),
                                        itemname=rd['data'][k]['name']).save()
                            count += 1
                            print count
                        i += 1
            else:
                _getlog('MarketShare/netmarketshare Get wrong response.cookie:'+ str(cookies) + '\n' + infomation[:100] + '...')
                errorcount += 1
        else:
            _getlog('MarketShare/netmarketshare Get ' + url + ' error try later,code:' + str(geturl.status_code))
            errorcount += 1
    _getlog('Get MarketShare/netmarketshare at %s . Finish:%d, Update%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))

#获取gs.statcounter.com上的信息
def getStatCounter():
    datemode = re.compile(r'% - (.+?)$')

    now = datetime.datetime.now()
    fromMonthYear = str(now.year - 1) + '-' + str(now.month)
    toMonthYear = str(now.year) + '-' + str(now.month)

    def cut(str):
        return ''.join(str.split('-'))

    def dateform(strdate):
        d = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'June': '06', 'July': '07', 'Aug': '08',
             'Sept': '09',
             'Oct': '10', 'Nov': '11', 'Dec': '12',}
        year = strdate[-4:]
        month = d[strdate[:-5]]
        return year + '-' + month

    fromInt = cut(fromMonthYear)
    toInt = cut(toMonthYear)
    regions = ['Worldwide', 'China']
    region_hiddens = ['ww', 'CN']

    devices = ['Desktop', 'Mobile']
    statTypes = ['Browser', 'Operating%20System']
    statType_hiddens = ['browser', 'os']
    count = skipcount = updatecount = errorcount = 0
    for device in devices:
        device_hidden = device.lower()
        for (statType, statType_hidden) in zip(statTypes, statType_hiddens):
            #该网站的一个合并chrome和firefox各版本的选择
            if device == 'Desktop' and statType == 'Browser':
                nstatType, nstatType_hidden = 'Combine%%20Chrome%%20(all%%20versions)%%20%%26%%20Firefox%%20(5%%2B)', \
                                              'browser_version_partially_combined'
            else:
                nstatType, nstatType_hidden = statType, statType_hidden

            for (region, region_hidden) in zip(regions, region_hiddens):
                url = "http://gs.statcounter.com/chart.php?device=%s&" \
                      "device_hidden=%s&multi-device=true&statType_hidden=%s&" \
                      "region_hidden=%s&granularity=monthly&statType=%s&" \
                      "region=%s&fromInt=%s&toInt=%s&fromMonthYear=%s&toMonthYear=%s" \
                      % (device, device_hidden, nstatType_hidden, region_hidden, nstatType, region, fromInt, toInt,
                         fromMonthYear, toMonthYear)
                header = {
                    "User-Agent":
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "+
                        "Chrome/54.0.2840.71 Safari/537.36"}
                try:
                    geturl = requests.get(url, headers=header)
                except ConnectionError as e:
                    _getlog('Error:'+str(e) +' in connect to '+ url)
                    continue

                if geturl.status_code == 200:
                    infomation = geturl.text
                    #xml接口
                    soup = BeautifulSoup(infomation, "xml")
                    datasets = soup.select('dataset')
                    if datasets:
                        for dataset in datasets:
                            for set in dataset.select('set'):
                                touch = MarketShare.objects.filter(
                                    date=dateform(datemode.findall(set.get('toolText'))[0]),
                                    source='http://gs.statcounter.com/', sourcename='statcounter',
                                    platform=device_hidden, myType=statType_hidden,
                                    market=region_hidden, itemname=dataset.get('seriesName'))
                                if touch:
                                    if  touch[0].value != float(set.get('value')):
                                        touch.update(value=float(set.get('value')))
                                        count += 1
                                        updatecount += 1
                                        print 'update'
                                    else:
                                        skipcount += 1
                                        print 'skip'
                                else:
                                    MarketShare(date=dateform(datemode.findall(set.get('toolText'))[0]),
                                                source='http://gs.statcounter.com/', sourcename='statcounter',
                                                platform=device_hidden, myType=statType_hidden,
                                                market=region_hidden, value=float(set.get('value')),
                                                itemname=dataset.get('seriesName')).save()
                                    count += 1
                                    print count
                    else:
                        _getlog('Get MarketShare/statcounter wrong response\n' + infomation[:100] + '...')
                        errorcount += 1
                else:
                    _getlog('Get MarketShare/statcounter' + url + ' error try later,code:' + str(geturl.status_code))
                    errorcount += 1
    _getlog('Get MarketShare/statcounter at %s . Finish:%d, Update:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))


def getAndroid():
    datamode = re.compile(r'"api": (\d+?),\n.+?"name": ".+?",\n.+?"perc": "(\d+?\.\d+?)"')
    datamode2 = re.compile(
        r'"api":(\d+?),\n.+?"link":\'<a href="https://developer.android.com/about/versions/.+?.html">(.+?)</a>')

    datemode = re.compile(r'ending on (\w+?) \d{1,2}, (\d{4}?).\n')

    url = "https://developer.android.com/about/dashboards/index.html"

    header = {
        "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"
    }

    def dateform(dategroup):
        d = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07',
             'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',}
        year = dategroup[1]
        month = d[dategroup[0]]
        return year + '-' + month

    try:
        geturl = requests.get(url, headers=header)
    except ConnectionError as e:
        _getlog('Error:'+str(e)+' in connect to '+url)
        return

    count = skipcount = updatecount = errorcount = 0
    if geturl.status_code == 200:
        infomation = geturl.text
        soup = BeautifulSoup(infomation, "lxml")
        text = soup.text
        VERSION_DATA = datamode.findall(text)
        VERSION_NAMES = datamode2.findall(text)
        timeframeDescription = soup.select('em')[0].get_text()
        DATE = dateform(datemode.findall(timeframeDescription)[0])
        if VERSION_DATA and VERSION_NAMES and DATE:
            for data in VERSION_DATA:
                for name in VERSION_NAMES:
                    if data[0] == name[0]:
                        touch = MarketShare.objects.filter(date=DATE,
                                                           source='https://developer.android.com/about/dashboards/index.html',
                                                           sourcename='安卓开发者论坛',
                                                           platform='mobile', myType='os',
                                                           market='ww',
                                                           itemname='Android' + ''.join(name[1].split('<br>')),
                                                           remarks=timeframeDescription)
                        if touch:
                            if  touch[0].value != float(data[1]):
                                touch.update(value=data[1])
                                count += 1
                                updatecount += 1
                                print 'update'
                            else:
                                skipcount += 1
                                print 'skip'
                        else:
                            MarketShare(date=DATE, source='https://developer.android.com/about/dashboards/index.html',
                                        sourcename='安卓开发者论坛',
                                        platform='mobile', myType='os',
                                        market='ww', value=data[1],
                                        itemname='Android' + ''.join(name[1].split('<br>')),
                                        remarks=timeframeDescription).save()
                            count += 1
                            print count
        else:
            _getlog('Get MarketShare/android wrong response\n' + text[:100] + '...')
            errorcount += 1
    else:
        _getlog('Get MarketShare/android ' + url + ' error try later,code:' + str(geturl.status_code))
        errorcount += 1

    _getlog('Get MarketShare/android at %s . Finish:%d, Update:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))


def getBaidu():
    # 采用时间戳（毫秒）的API格式，精确到天。

    now = datetime.datetime.now()
    stime = str(now.year - 1) + '-' + str(now.month)
    etime = str(now.year) + '-' + str(now.month) + '-' + str(now.day)
    st = int(time.mktime(datetime.datetime.strptime(stime, "%Y-%m").timetuple()) * 1000)
    et = int(time.mktime(datetime.datetime.strptime(etime, "%Y-%m-%d").timetuple()) * 1000)

    myTypes = ['os', 'browser']
    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; " \
              "name=\"st\"\r\n\r\n%d\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; " \
              "name=\"et\"\r\n\r\n%d\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; " \
              "name=\"sm\"\r\n\r\n2014/10\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; " \
              "name=\"reportId\"\r\n\r\n200\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" % (st, et)

    headers = {
        'content-myType': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'cache-control': "no-cache",
        'postman-token': "00da87ee-40fb-e2c7-7747-e75444100e18"
    }
    count = skipcount = updatecount = errorcount = 0
    for myType in myTypes:
        url = "http://tongji.baidu.com/data/%s/getData" % myType
        source = "http://tongji.baidu.com/data/%s" % myType
        try:
            response = requests.request("POST", url, data=payload, headers=headers)
        except ConnectionError as e:
            _getlog('Error:'+str(e)+' in connect to '+url+str(payload))
            continue

        if response.status_code == 200:
            content = json.loads(response.text)
            if content.has_key('status'):
                if content['status'] == 0:
                    if myType == 'browser':
                        cv = content['data']['version']
                    else:
                        cv = content['data']
                    i = 0
                    while i < len(cv['names']):
                        j = 0
                        while j < len(cv['dates']):
                            touch = MarketShare.objects.filter(date=cv['dates'][j].replace('.', '-'), source=source,
                                                               sourcename='百度移动流量研究院', platform='desktop',
                                                               myType=myType,
                                                               market='CN', itemname=cv['names'][i])
                            if touch:
                                if  touch[0].value != float(cv['datas'][i]['pvs'][j]):
                                    touch.update(value=cv['datas'][i]['pvs'][j])
                                    count += 1
                                    updatecount += 1
                                    print 'update'
                                else:
                                    skipcount += 1
                                    print 'skip'
                            else:
                                MarketShare(date=cv['dates'][j].replace('.', '-'), source=source,
                                            sourcename='百度移动流量研究院',
                                            platform='desktop', myType=myType,
                                            market='CN', value=cv['datas'][i]['pvs'][j],
                                            itemname=cv['names'][i],
                                            remarks='来源于百度统计所覆盖的超过150万的站点，而不是baidu.com的流量数据。').save()
                                count += 1
                                print count
                            j += 1
                        i += 1
                else:
                    _getlog('Get MarketShare/Baidu wrong status\n' + content[:100] + '...')
                    errorcount += 1
            else:
                _getlog('Get MarketShare/Baidu wrong response\n' + content[:100] + '...')
                errorcount += 1
        else:
            _getlog('Get MarketShare/Baidu ' + url + ' error try later,code:' + str(response.status_code))
            errorcount += 1

    _getlog('Get MarketShare/Baidu at %s . Finish:%d, Update:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))


def getBaiduNew():
    # 时间戳（秒），更新频率暂时未知。原始数据为2016年10月1日

    stattime = 1475251200
    rankurl = "https://mtj.baidu.com/data/mobile/rank"
    trendurl = "https://mtj.baidu.com/data/mobile/trend"

    headers = {
        'cache-control': "no-cache",
        'postman-token': "c69101df-f2dc-f034-5310-5ade853e7eea"
    }

    def dateform(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m')

    pd = {'iOS': 1, 'Android': 0}

    count = skipcount = updatecount = errorcount = 0
    for k in pd:
        platformId = pd[k]

        querystring = {"dimension": "os", "platformId": platformId, "stattime": stattime}
        try:
            response = requests.request("GET", rankurl, headers=headers, params=querystring)
        except ConnectionError as e:
            _getlog('Error:'+str(e)+' in connect to '+rankurl+str(querystring))
            continue
        if response.status_code == 200:
            result = (json.loads(response.text))['result']
            if len(result['id']) == len(result['name']):
                for (i, id) in enumerate(result['id']):
                    trendquerystring = {"dimension": "os", "platformId": platformId, "rankId": id, "stattime": stattime}
                    try:
                        trendresponse = requests.request("GET", trendurl, headers=headers, params=trendquerystring)
                    except ConnectionError as e:
                        _getlog('Error:' + str(e) + ' in connect to ' + trendurl + str(trendquerystring))
                        continue
                    MarketShare.objects.filter(sourcename='百度移动流量研究院-' + k, platform='moblie', myType='os',
                                               itemname=result['name'][i]).all().delete()
                    trendresult = (json.loads(trendresponse.text))['result']
                    if len(trendresult['scale']) == len(trendresult['name']):

                        for (j, scale) in enumerate(trendresult['scale']):
                            if scale == '-':
                                value = 0
                            else:
                                value = scale
                            touch = MarketShare.objects.filter(date=dateform(trendresult['name'][j]),
                                                               sourcename='百度移动流量研究院-' + k,
                                                               platform='mobile', myType='os', market='CN', value=value,
                                                               itemname=result['name'][i])
                            if touch:
                                if  touch[0].value != float(value):
                                    touch.update(value=value)
                                    count += 1
                                    updatecount += 1
                                    print 'update'
                                else:
                                    skipcount += 1
                                    print 'skip'
                            else:
                                MarketShare(date=dateform(trendresult['name'][j]),
                                            source="https://mtj.baidu.com/data/mobile/device",
                                            sourcename='百度移动流量研究院-' + k,
                                            platform='mobile', myType='os',
                                            market='CN', value=value,
                                            itemname=result['name'][i],
                                            remarks='来源于百度统计所覆盖的超过150万的站点，而不是baidu.com的流量数据。').save()
                                count += 1
                                print count
                    else:
                        _getlog('Get MarketShare/BaiduNew' + trendurl + ' scale-name error\n' + trendresponse.text[:100] + '...')
                        errorcount += 1
            else:
                _getlog('Get MarketShare/BaiduNew ' + rankurl + ' id-name error\n' + response.text[:100] + '...')
                errorcount += 1
        else:
            _getlog('Get MarketShare/Ios ' + rankurl + ' ' + str(response.status_code))
    _getlog('Get MarketShare/BaiduNew at %s . Finish:%d, Update:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))


def getIos():
    # 每月更新一次

    datamode = re.compile(r'\{name:"(.+?)", value:(\d{1,2}),')
    datemode = re.compile(r'^(\w+?) \d{1,2}, (\d{4})\.$')

    url1 = "https://developer.apple.com/support/app-store/"
    url2 = "https://developer.apple.com/support/includes/ios-chart/scripts/chart.js"

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36"}

    def dateform(dategroup):
        d = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06', 'July': '07',
             'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12',}
        year = dategroup[1]
        month = d[dategroup[0]]
        return year + '-' + month
    try:
        geturl = requests.get(url1, headers=header)
    except ConnectionError as e:
        _getlog(str(e))
        return
    count = skipcount = errorcount = updatecount = 0

    if geturl.status_code == 200:
        infomation = geturl.text
        soup = BeautifulSoup(infomation, "lxml")
        remarks = soup.select('#main > section.grid > section > article > div > section.col-33 > div > div > p')[
            0].get_text()
        DATE = dateform(datemode.findall(soup.select('p > span.nowrap')[0].get_text())[0])

        try:
            geturl = requests.get(url2, headers=header)
        except ConnectionError as e:
            _getlog(str(e))
            return

        if geturl.status_code == 200:
            infomation = geturl.text
            datas = datamode.findall(infomation)
            for data in datas:
                touch = MarketShare.objects.filter(date=DATE, source=url1, sourcename='IOS开发者论坛',
                                                   platform='mobile', myType='os', market='ww', itemname=data[0],
                                                   remarks=remarks)
                if touch:
                    if touch[0].value != float(data[1]):
                        touch.update(value=data[1])
                        updatecount += 1
                        count += 1
                        print 'update'
                    else:
                        skipcount += 1
                        print 'skip'
                else:
                    MarketShare(date=DATE, source=url1,
                                sourcename='IOS开发者论坛',
                                platform='mobile', myType='os',
                                market='ww', value=data[1],
                                itemname=data[0],
                                remarks=remarks).save()
                    count += 1
                    print count
        else:
            _getlog('Get MarketShare/Ios '+ url2 +' '+ str(geturl.status_code))
            errorcount += 1
    else:
        _getlog('Get MarketShare/Ios ' + url1 + ' ' + str(geturl.status_code))
        errorcount += 1
    _getlog('Get MarketShare/Ios at %s . Finish:%d, Update:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, skipcount, errorcount))



def getLi(endDate):
    url = "http://analyzer2.corp.youdao.com/server-run/run-script.html"
    backDaysd = {'D': 1, 'W': 7, 'M': 30}


    count = getnonecount = updatecount = skipcount = errorcount = 0

    for datetype in backDaysd.keys():
        print datetype
        headers = {
            'cache-control': "no-cache",
            'postman-token': "49a05dc4-4054-1c8b-e595-b92424e95ce3"
        }
        conn = httplib.HTTPConnection("analyzer2.corp.youdao.com")
        url = "/server-run/run-script.html?scriptId=deviceDist&isAsync=true&backDays=%d&endDate=%s" % \
              (backDaysd[datetype], endDate)
        try:
            conn.request("GET", url, headers=headers)

        except ConnectionError as e:
            _getlog('Error:'+str(e)+' in connect to ' + url )
            continue
        except Timeout as e:
            _getlog('Warning:' + str(e) + ' in connect to ' + url )
            continue

        r1 = conn.getresponse()
        try:
            rptext = json.loads(r1.read())
        except ValueError as e:
            _getlog(str(e) + ': \n ' + r1.read()[:100] + '...')

        if rptext.has_key('result'):
            for item in rptext['result']:
                title = (item['title'].split(' - '))
                if item['kvs'][0].has_key('msg'):
                    getnonecount += 1
                else:
                    myType = title[-1]
                    platform = title[-2]
                    productname = title[-3]
                    for kv in item['kvs']:
                        touch = ProductsShare.objects.filter(productname=productname, platform=platform,
                                                            myType=myType, remarks='', datetype=datetype,
                                                            itemname=kv[myType] or 'other',
                                                            date=endDate)
                        if len(touch) == 1 :
                            if(touch[0].pv != int(kv['pv']) or touch[0].uv != int(kv['uv'])):
                                touch.update(pv=kv['pv'], uv=kv['uv'])
                                count += 1
                                updatecount += 1
                                print 'update'
                            else:
                                skipcount += 1
                                print 'skip'
                        elif len(touch) > 1:
                            errorcount += 1
                        else:
                            ProductsShare(productname=productname.lower(), platform=platform, myType=myType, remarks='',
                                          pv=kv['pv'], uv=kv['uv'], itemname=kv[myType] or 'other',
                                          date=endDate, datetype=datetype).save()
                            count += 1
                            print count
        else:
            _getlog('Get ProductsShare/Li has no result\n'+ rptext[:100] + '...')
            errorcount += 1

    _getlog('Get ProductsShare/Li at %s . Finish:%d, Update:%d, Getnone:%d, Skip:%d, Error:%d' %
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count, updatecount, getnonecount, skipcount, errorcount))
