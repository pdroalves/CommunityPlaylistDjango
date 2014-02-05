# -*- coding: utf-8 -*-
##    Author: 
#       Pedro Alves, pdroalves@gmail.com
#               01 February, 2014 - Campinas,SP - Brazil

import logging
from models import Channel,Playlist,Vote
logger = logging.getLogger("DBManager")


class DatabaseManager:
	def __init__(self,channel):
		assert channel is not None
		# If this channel doesn't exists, this exception should be catched outside this class
		self.channel = Channel.objects.get(id=channel)
		self.playlist = Playlist
		self.vote = Vote
		logger.info("Database manager started")

	def get_current_background(self):
		return self.channel.background
		
	def set_background(self,background):
		assert type(background) == str or type(background) == unicode
		self.channel.background = background
		self.channel.save()

	def get_playlist(self):
		result = self.playlist.objects.filter(channel=self.channel,played=False,removed=False)
		result.order_by('id')
		result_formatted = [[	video.id,
								video.url]
							for video in result]
		return result_formatted

	def get_votes(self):
		pl = self.playlist.objects.filter(channel=self.channel,played=False,removed=False)
		result = self.vote.objects.filter(video=pl,video__played=False,video__removed=False).order_by('created_at')

		result_formatted = [[	vote.video.url,
								vote.tag,
								vote.positive,
								vote.negative]
							for vote in result]
		return result_formatted

	def add_video(self,url,creator):
		video = self.channel.playlist_set.create(url=url)
		video.save()
		video.vote_set.create(tag=creator,positive=1)
		return True

	def add_vote(self,url,creator,positive,negative):
		video = self.playlist.objects.get(channel=self.channel,url=url)
		video.vote_set.create(tag=creator,positive=positive,negative=negative)
		return True

	def rm_video(self,url):
		video = self.playlist.objects.get(channel=self.channel,url=url)
		if video is not None:
			video.delete()
		else:
			return False
		return True

	def clear_all(self):
		self.playlist.objects.filter(	channel=self.channel,
										played=False,
										removed=False).update(removed=True)


	def mark_video_played(self,url):
		video = self.playlist.objects.get(channel=self.channel,url=url,played=False,removed=False)
		video.played = True
		video.save()