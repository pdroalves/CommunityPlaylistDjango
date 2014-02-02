# -*- coding: utf-8 -*-
##    Author: 
#       Pedro Alves, pdroalves@gmail.com
#               01 February, 2014 - Campinas,SP - Brazil

import logging
from models import Playlist,Vote
logger = logging.getLogger("DBManager")


class DatabaseManager:
	__instance = None

	# This is a singleton
	def __new__(cls,*args,**kwargs):
		if not cls.__instance:
			cls.__instance = super(DatabaseManager,cls).__new__(cls,*args,**kwargs)
		return cls.__instance

	def __init__(self):
		self.playlist = Playlist
		self.vote = Vote
		logger.info("Database manager started")

	def get_playlist(self):
		result = self.playlist.objects.filter(played=False,removed=False)
		result.order_by('id')
		result_formatted = [[	video.id,
								video.url]
							for video in result]
		return result_formatted

	def get_votes(self):
		result = self.vote.objects.filter(video__played=False,video__removed=False).order_by('created_at')

		result_formatted = [[	vote.video.url,
								vote.tag,
								vote.positive,
								vote.negative]
							for vote in result]
		return result_formatted

	def add_video(self,url,creator):
		video = self.playlist(url=url)
		video.save()
		video.vote_set.create(tag=creator,positive=1)
		return True

	def add_vote(self,url,creator,positive,negative):
		video = self.playlist.objects.get(url=url)
		video.vote_set.create(tag=creator,positive=positive,negative=negative)


	def rm_video(self,url):
		video = self.playlist.objects.get(url=url)
		if video is not None:
			video.delete()
		else:
			return False
		return True

	def clear_all(self):
		self.playlist.objects.filter(played=False,removed=False).update(removed=True)


	def mark_video_played(self,url):
		video = self.playlist.objects.get(url=url)
		video.played = 1

