# -*- coding: utf-8 -*-
import json
import os
import re
import string
import logging
from queue_manager import QueueManager
from database_manager import DatabaseManager
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger("ChannelsViews")
#####################################
######## SUPPORT METHODS ############


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

def __get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

####################################
############# VIEWS ################

def index(request,channel_id):
    global current_background
    backgrounds,backgrounds_directory = __get_backgrounds()
    context = { "title":__get_title(),
                "backgrounds":backgrounds,
                "current_background":'',
                "CHANNEL_ID":channel_id
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
            return redirect('index',channel_id)
        else:
            # Return a 'disabled account' error message
            return redirect('index',channel_id)
    else:
        # Return an 'invalid login' error message.
        return redirect('index',channel_id)

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
    return HttpResponse(json.dumps(
                {"queue":queue.getQueue(),
                "current_background":get_current_background(channel = channel_id),
                "backgrounds":backgrounds
                }
            ))

def next(request,channel_id):
    queue = QueueManager(channel = channel_id)
    video_url = queue.next()
    if video_url is not None:
        return HttpResponse(json.dumps(video_url))
    else:
        settings = __load_settings()
        return HttpResponse(json.dumps(settings['standardEndVideoId']))

def add(request,channel_id):
    queue = QueueManager(channel = channel_id)

    # Remove non-printable chars
    element = request.GET['element']
    creator = __get_client_ip(request)
    url = filter(lambda x: x in string.printable,element)

    match = re.search('.*[w][a][t][c][h].[v][=]([^/,&]*)',url)
    if match:
        queue.add(url=match.group(1),creator=creator)
        logger.info('Added '+url)
        return HttpResponse(1)
    else:
        logger.critical('Error! URL Invalid '+url)
        return HttpResponse(0)

def rm(request,channel_id):
    queue = QueueManager(channel = channel_id)

    url = request.GET['element']
    logger.info('Removing '+url)
    queue.rm(url)
    return HttpResponse(1)

def vote(request,channel_id):
    queue = QueueManager(channel = channel_id)

    url = request.GET('url')
    positive = int(request.GET('positive'))
    negative = int(request.GET('negative'))
    creator = __get_client_ip(request)

    r = queue.register_vote(    url=url,
                                positive=positive,
                                negative=negative,
                                creator=creator
                            )
    if not r:
        logger.critical("Error on vote.")        
        #flash("Seu voto não pôde ser registrado. Tente novamente.","error") #To-Do

def get_current_background(channel):
    dbm = DatabaseManager(channel = channel)
    return dbm.get_current_background()

def set_background(request,channel_id):
    dbm = DatabaseManager(channel = channel_id)
    new_background = request.GET['new_background']
    dbm.set_background(background=new_background)
    return HttpResponse(1)  