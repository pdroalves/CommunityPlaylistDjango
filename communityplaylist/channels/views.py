# -*- coding: utf-8 -*-
import json
import os
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse

current_background = ''

# Create your views here.
def __load_settings(path="/static/settings.json"):
    #with open(path) as f:
    #    settings = json.load(f)
    data = """{"standardStartVideoId": "dQw4w9WgXcQ",
 "backgrounds_path": "/home/pedro/Projetos/CommunityPlaylistDjango/communityplaylist/channels/static/backgrounds",
 "background": "realidade_aumentada.jpg",
 "standardEndVideoId": "F0BfcdPKw8E",
 "title": "CommunityPlaylist"}"""
    settings = json.loads(data)
    return settings

def get_title():
    settings = __load_settings()
    return settings['title']

def get_backgrounds():
    settings = __load_settings()
    backgrounds_directory = settings['backgrounds_path']
    backgrounds = os.listdir(backgrounds_directory)
    if backgrounds is not None:
        backgrounds.sort()
    print backgrounds
    return backgrounds

def index(request):
    global current_background
    context = { "title":get_title(),
                "backgrounds":get_backgrounds(),
                "current_background":current_background
                }
    return render(request,'channels/index.html',context)

def log_in(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
            return redirect('index')
        else:
            # Return a 'disabled account' error message
            return redirect('index')
    else:
        # Return an 'invalid login' error message.
        return redirect('index')

def log_out(request):
    if request.user.is_authenticated():
        logout(request)
        return redirect('index')
    else:
        return redirect('index')
