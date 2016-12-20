from django.shortcuts import render
from django.http import HttpResponse
from apiget.models import information
import json
from django.shortcuts import render
from itest.settings import BASE_DIR
from django.contrib.auth.decorators import login_required

def _cinit():
    timefile = open('%s/time.txt' % BASE_DIR, 'r')
    content = {}
    content['uptime'] = timefile.read()
    timefile.close()
    return content

def _mcget(request,content):
    if 'mode' in request.GET:
        mode = request.GET['mode']
        content['mode'] = mode
    if 'case' in request.GET:
        case = request.GET['case']
        content['case'] = case
    return content

def home(request):
    content = _cinit()
    return render(request, 'table.html', content)

def charts(request):
    content = _cinit()
    return render(request, 'charts.html', content)

def quarterreview(request):
    content = _cinit()
    content = _mcget(request,content)

    return render(request, 'quarterreview.html', content)

def productreview(request):
    content = _cinit()
    content = _mcget(request, content)

    return render(request, 'productreview.html', content)

def feedback(request):
    content = _cinit()
    content = _mcget(request, content)

    return render(request, 'feedback.html', content)


def update(request):
    content = _cinit()
    content = _mcget(request, content)

    return render(request, 'update.html', content)


def uploadpage(request):
    content = _cinit()
    content = _mcget(request, content)

    return render(request, 'fbupload.html', content)


def downloadpage(request):
    content = _cinit()
    content = _mcget(request, content)

    return render(request, 'filedown.html', content)

def marketshare(request):
    content = _cinit()

    return render(request, 'marketshare.html', content)

def productsshare(request):
    content = _cinit()

    return render(request, 'productsshare.html', content)