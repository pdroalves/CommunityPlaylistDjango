# -*- coding: utf-8 -*-
import json
import os
from queue_manager import QueueManager
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Create your views here.
def __load_settings(path="settings.json"):
    with open(os.path.join(PROJECT_ROOT,path)) as f:
       settings = json.load(f)
    return settings

def __get_title():
    settings = __load_settings()
    return settings['title']

def __get_backgrounds():
    settings = __load_settings()
    backgrounds_directory = os.path.join(PROJECT_ROOT,settings['backgrounds_path'])
    backgrounds = os.listdir(backgrounds_directory)
    if backgrounds is not None:
        backgrounds.sort()
    print backgrounds
    return backgrounds,backgrounds_directory

def __get_current_background():
    # To-do
    return ''

def index(request,channel_id):
    global current_background
    backgrounds,backgrounds_directory = __get_backgrounds()
    context = { "title":__get_title(),
                "backgrounds":backgrounds,
                "current_background":'',
                "channel":channel_id
                }
    return render(request,'channels/index.html',context)

def log_in(request,channel_id):
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

def log_out(request,channel_id):
    if request.user.is_authenticated():
        logout(request)
        return redirect('index')
    else:
        return redirect('index')

def update(request,channel_id):
    queue = QueueManager(channel = channel_id)
    queue.sort()

    backgrounds,backgrounds_directory = __get_backgrounds()
    return json.dumps(
                {"queue":queue.getQueue(),
                "current_background":__get_current_background(),
                "backgrounds_directory":backgrounds_directory,
                "backgrounds":backgrounds
                }
            )



