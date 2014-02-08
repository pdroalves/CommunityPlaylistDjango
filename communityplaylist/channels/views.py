# -*- coding: utf-8 -*-
import json
import os
import re
import string
import logging
import time
from queue_manager import QueueManager
from database_manager import DatabaseManager
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from django.core.cache import cache

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger("ChannelsViews")

#####################################
######## SUPPORT METHODS ############
class Clock:
    start_timer = 0
    def __init__(self,logger):
        self.logger =logger
    def start(self):
        self.start_timer = time.time()
    def stop(self):
        if self.start_timer > 0:
            start = self.start_timer
            self.start_timer = 0
            return time.time() - start
        else:
            return 0

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
    clock = Clock(logger=logger)
    clock.start()
    global current_background
    backgrounds,backgrounds_directory = __get_backgrounds()
    dbm = DatabaseManager(channel = channel_id)
    context = { "title":dbm.get_title(),
                "backgrounds":backgrounds,
                "current_background":'',
                "channel_id":channel_id
                }
    logger.info("Index returned in %f seconds" % clock.stop())
    return render(request,'channels/index.html',context)

def log_in(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    logger.info("Login returned in %f seconds" % clock.stop())
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
    clock = Clock(logger=logger)
    clock.start()
    if request.user.is_authenticated():
        logout(request)
        logger.info("Logout returned in %f seconds" % clock.stop())
        return redirect('index',channel_id)
    else:
        logger.info("Logout returned in %f seconds" % clock.stop())
	return redirect('index',channel_id)

def update(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    queue = QueueManager(channel = channel_id)
    queue.sort()

    backgrounds,backgrounds_directory = __get_backgrounds()
    logger.info("Update returned in %f seconds" % clock.stop())
    return HttpResponse(json.dumps(
                {"queue":queue.getQueue(),
                "current_background":get_current_background(channel = channel_id),
                "backgrounds":backgrounds
                }
            ))

def next(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    queue = QueueManager(channel = channel_id)
    video_url = queue.next()
    if video_url is not None:
        logger.info("Next returned in %f seconds" % clock.stop())
        return HttpResponse(json.dumps(video_url))
    else:
        settings = __load_settings()
        logger.info("Next returned in %f seconds" % clock.stop())
        return HttpResponse(json.dumps(settings['standardEndVideoId']))

def add(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    queue = QueueManager(channel = channel_id)

    # Remove non-printable chars
    element = request.GET['element']
    creator = __get_client_ip(request)
    url = filter(lambda x: x in string.printable,element)

    match = re.search('.*[w][a][t][c][h].[v][=]([^/,&]*)',url)
    if match:
        queue.add(url=match.group(1),creator=creator)
        logger.info('Added '+url)
        logger.info("add returned in %f seconds" % clock.stop())
        return HttpResponse(1)
    else:
        logger.critical('Error! URL Invalid '+url)
        logger.info("add returned in %f seconds" % clock.stop())
        return HttpResponse(0)

def rm(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    queue = QueueManager(channel = channel_id)

    url = request.GET['element']
    logger.info('Removing '+url)
    queue.rm(url)
    logger.info("rm returned in %f seconds" % clock.stop())
    return HttpResponse(1)

def vote(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
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
        #flash("Seu voto não pôde ser registrado. Tente novamente.","error") #To-
        logger.info("rm returned in %f seconds" % clock.stop())
        return HttpResponse(0)

    logger.info("vote returned in %f seconds" % clock.stop())
    return HttpResponse(1)

def get_current_background(channel):
    clock = Clock(logger=logger)
    clock.start()
    dbm = DatabaseManager(channel = channel)
    logger.info("get_current_background returned in %f seconds" % clock.stop())
    return dbm.get_current_background()

def set_background(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    dbm = DatabaseManager(channel = channel_id)
    new_background = request.GET['new_background']
    dbm.set_background(background=new_background)
    logger.info("set_background returned in %f seconds" % clock.stop())
    return HttpResponse(1)  

def set_playing(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    now_playing = {
            'title':request.GET['title'],
            'now_playing':request.GET['now_playing'],
            'song_id':request.GET['song_id'],
            'song_playing':request.GET['song_playing'],
            'current_time':request.GET['current_time']
    }
    cache.set('now_playing',now_playing)
    logger.info("set_playing returned in %f seconds" % clock.stop())
    return HttpResponse(1)

def get_playing(request,channel_id):
    clock = Clock(logger=logger)
    clock.start()
    if not cache.has_key('now_playing'):
        now_playing = { 'title':'Empty',
                        'now_playing':-1,
                        'song_id':'Empty',
                        'song_playing':'Empty',
                        'current_time':0
                        }          
    else:
        now_playing = cache.get('now_playing')
    
    logger.info("Now playing: "+str(now_playing['song_playing']))
    logger.info("get_playing returned in %f seconds" % clock.stop())
    return HttpResponse(json.dumps(now_playing))
