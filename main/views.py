from django.shortcuts import render
import os
import logging

# Create your views here.
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger("MainView")

def index(request):
	context = {"title":"CommunityPlaylist"}
	return render(request,'main/index.html',context)