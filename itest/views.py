from django.shortcuts import render
from django.http import HttpResponse
from apiget.models import information
import json
from django.shortcuts import render
def home(request):
    return render(request, 'test.html')