# -*- coding: utf-8 -*-
##    Author: 
#       Pedro Alves, pdroalves@gmail.com
#               01 February, 2014 - Campinas,SP - Brazil

import sqlite3
import time
import logging
import string
from youtube_handler import YoutubeHandler
from database_manager import DatabaseManager


logger = logging.getLogger("QueueManager")

class QueueManager:

	def __init__(self,channel):
		assert channel is not None
		self.queue = []
		self.db_manager = DatabaseManager(channel=channel)
		self.conn = None
		self.yth = YoutubeHandler()
		self.__start_pause_ts=0
		logger.info("Queue started")

	def __exit__(self, type, value, traceback):
		db = self.get_db()
		db.commit()
		logger.info("Queue finished")

	def calc_playtime(self,url,min_starvation_time=1200):
		# Calculate how long until this song start to play without any queue order change
		assert type(url) == str
		candidates = [x for x in self.queue if x.get('url') != url]
		playtime = 0
		
		for candidate in candidates:
			try:
				playtime += candidate.get("data").get("duration")
			except Exception,err:
				if candidate is None:
					logger.critical("Candidate is null.\n\t%s" % candidates)
				elif not candidate.has_key("data"):
					logger.critical("Candidate %s doesn't have 'data' field" % candidate)
				elif type(candidate.get("data")) != dict:
					logger.critical("Candidate 'data' is weird. It is not a dict.")
				elif not candidate.get("data").has_key("duration"):
					logger.critical("Candidate %s doesn't have 'duration' field" % candidate)
				logger.critical(str(err))
		return max(playtime,min_starvation_time)


	def calc_full_playtime(self):
		queue_length = len(self.queue)
		if queue_length > 0:
			return self.calc_playtime(url=str(self.queue[queue_length-1].get("url")))
		else:
			return 0


	def get_db(self):
		if self.conn is None:
			print "Starting database."
			self.conn = self.db_manager

			history = self.conn.get_playlist()
			voters_gross = self.conn.get_votes()

			voters = dict()
			for vote in voters_gross:
				url = vote[0]
				tag = vote[1]
				positive = vote[2]
				negative = vote[3]

				if url not in voters.keys():
					voters[url] = dict()

				if positive:
					voters[url][tag] = 1
				elif negative:
					voters[url][tag] = -1

			voters_history = dict()
			for url in voters.keys():
				if not voters_history.has_key(url):
					voters_history.update({url:{"positive":[],"negative":[]}})

				for tag in voters[url]:
					if voters[url][tag] > 0 and tag not in voters_history[url]["positive"]:
						voters_history[url]["positive"].append(tag)
						if tag in voters_history[url]["negative"]:
							voters_history[url]["negative"].remove(tag)
					if voters[url][tag] < 0 and tag not in voters_history[url]["negative"]:
						voters_history[url]["negative"].append(tag)	
						if tag in voters_history[url]["positive"]:
							voters_history[url]["positive"].remove(tag)					

			txt = "Votes founded: %d"%len(voters_history.keys())
			logger.info(txt)
			for h in history:
				print h
				id = h[0]
				url = filter(lambda x: x in string.printable,h[1])
				if voters_history.has_key(url):
					positive_voters = voters_history[url]["positive"]
					negative_voters = voters_history[url]["negative"]
				else:
					logger.info("No votes for "+str(url))
					positive_voters = []
					negative_voters = []

				# The need to receive data from Youtube makes this step slow
				data = self.yth.get_info(url) 
				try:
					if type(data) is not dict:
						ytData = data.json()
					else:
						ytData = data

					self.queue.append({
									"id":id,
									"url":url,
									"added_at":int(time.time()),
									"playtime":self.calc_full_playtime(),	
									"voters":{
										"positive":positive_voters,
										"negative":negative_voters
									},
									"data":ytData.get('data')
									})
				except Exception,err:
					txt ="Url: %s - Data: %s" % (url,str(data))
					logger.critical(str(err))
					logger.critical(txt)
			logger.info("DB loaded:\n\t"+str(self.queue))
		return self.conn

	def add(self,url,creator):
		## Returns boolean,boolean
		# The first boolean is true if the url is in the queue
		# The second boolean is true if the url was added to the queue at this step. 
		#    False if it was already there.
		
		db = self.get_db()

		new_item = None
		done = False

		# Checks that this urls isnt already in queue
		url_in_queue = [element for element in self.queue if element['url'] == url]

		if len(url_in_queue) == 0:
			txt = "Video %s added by %s" %(url,creator)
			print txt
			logger.info(txt)

			db.add_video(url=url,creator=creator)

			data = self.yth.get_info(url)
			if data is not None:
				if not type(data) == dict:
					ytData = data.json()
				else:
					ytData = data
				#print ytData.get("data").get("title")
				try:
					data = ytData.get('data')

					new_item = {
								"id":id,
								"url":url,
								"added_at":int(time.time()),
								"playtime":self.calc_full_playtime(),
								"voters":{
									"positive":[creator],
									"negative":[]
								},
								"data":ytData.get('data')
							}
					self.queue.append(new_item)
					logger.info("Item added: "+str(new_item))
				except Exception,err:
					logger.critical(str(err))
					logger.critical("Url: %s - Data: %s" % str(url,data))
			else:
				logger.critical("Couldn't add item %s"%url)
		else:
			return True,False
		return True,True

	def rm(self,url):
		assert type(url) == str
		logger.info("Clearing element "+url)
		db = self.get_db()
		candidates = [item for item in self.queue if item.get('url') == url]
		if len(candidates) > 0:
			element = candidates[0]
			self.queue.remove(element)
			status = db.rm_video(url=url)
			if status:
				logger.info("Item removed: "+str(element))
			else:
				logger.critical("Item wasn't found in database to be removed: "+url)	
				return False
		else:
			logger.critical("Item wasn't found to be removed: "+url)			
			return False
		return True

	def next(self):
		db = self.get_db()

		if(len(self.queue) > 0):
			next_element = self.queue[0]
			self.queue.remove(next_element)
			url = next_element['url']

			db.mark_video_played(url=url)

			status_txt = "Next song: "+str(url)
			logger.info(status_txt)

			return url
		else:
			return None

	def register_vote(self,url,positive,negative,creator):
		assert type(creator) == str
		assert type(positive) == int
		assert type(negative) == int
		try:
			db = self.get_db()
			candidates = [item for item in self.queue if item.get('url') == url]

			assert len(candidates) > 0
			
			element = candidates[0]

			# Update voters
			voters = element["voters"]
			if positive > 0 and creator not in voters.get("positive"):
				voters.get("positive").append(creator)
				if creator in voters.get("negative"):
					voters.get("negative").remove(creator)
			elif positive > 0 and creator in voters.get("positive"):
				raise Exception("Voto  positivo já registrado!")

			if negative > 0 and creator not in voters.get("negative"):
				voters.get("negative").append(creator)
				if creator in voters.get("positive"):
					voters.get("positive").remove(creator)
			elif negative > 0 and creator in voters.get("negative"):
				raise Exception("Voto negativo já registrado!")

			element.update({"voters":voters})
			db.add_vote(url=url,creator=creator,positive=positive,negative=negative)
			logger.info("Updating votes for "+str(element.get("url"))+": "+str(voters))
		except Exception,err:
			logger.critical("Error on vote register: \t%s"%str(err))
			return False
		return True

	def update_playtime(self):
		diff = 0
		if self.__start_pause_ts == 0:
			self.__start_pause_ts = time.time()

		if self.paused:
			logger.info("Queue paused")
			if time.time()-self.__start_pause_ts > 2:
				diff = time.time()-self.__start_pause_ts
				self.__start_pause_ts = time.time()
		elif self.__start_pause_ts > 0:
			diff = time.time()-self.__start_pause_ts
			logger.info("Queue resumed") 
			self.__start_pause_ts = 0

		if diff > 0.1:
			for element in self.queue:
				logger.info("Adding %s to %s playtime." % (diff,element.get("url")))
				element.update({"playtime":element.get("playtime")+diff})

	def set_pause(self,paused):
		self.paused = paused
		self.update_playtime()

	def getQueue(self):
		db = self.get_db() # Just asserts that there is something inside the db
		fila = []
		if len(self.queue) > 0:
			fila += [{
						"url":element.get('url'),
						"title":element.get('data').get('title'),
						"duration":element.get('data').get('duration'),
						"positive":len(element.get('voters').get('positive')),
						"negative":len(element.get('voters').get('negative'))
					} for element in self.queue]
		return fila

	def clear(self):
		txt = "Clearing list"
		logger.info(txt)
		print txt
		
		db = self.get_db()

		db.clear_all()		
		self.queue = list()

		logger.info("Queue cleared.")
		return

	def __is_starving(self,element,starvation_rate=2,min_starvation_time=0):
		assert element.has_key("added_at")
		assert element.has_key("playtime")
		assert element.has_key("data")
		if not element.get("data").has_key("duration"):
			duration = 120
		else:
			duration = element.get("data").get("duration")

		return time.time() - element.get("added_at")-element.get("playtime")*starvation_rate-duration > min_starvation_time

	def __custom_sort(self,starvation_rate=3):
		self.update_playtime()

		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		#lambda_starvation = lambda x: self.__is_starving(element=x,starvation_rate=starvation_rate)
		lambda_starvation = lambda x: False
		
		hungry = [x for x in self.queue if lambda_starvation(x)]

		if len(hungry) > 0:
			print ','.join([x.get("data").get("title")+"Playtime: "+str(x.get("playtime"))+" Starvation:"+str(lambda_starvation(x)) for x in hungry])

		if len(hungry) > 1:
			for x,y in zip(hungry,hungry[1:]):
				self.queue[self.queue.index(x)+1:self.queue.index(y)-1] = sorted(self.queue[self.queue.index(x)+1:self.queue.index(y)-1],key=lambda_votes,reverse=True)
		elif len(hungry) == 1:
			x = hungry[0]
			self.queue[0:self.queue.index(x)-1] = sorted(self.queue[0:self.queue.index(x)-1],key=lambda_votes,reverse=True)
			self.queue[self.queue.index(x)+1:len(self.queue)] = sorted(self.queue[self.queue.index(x)+1:len(self.queue)],key=lambda_votes,reverse=True)
		else:
			self.queue[0:len(self.queue)] = sorted(self.queue[0:len(self.queue)],key=lambda_votes,reverse=True)	
		logger.info("Sorting queue")
		return True,hungry

	def sort(self):
		# Ordena a fila de acordo com o tempo de espera e a quantidade de votos
		lambda_votes = lambda x:len(x.get("voters").get("positive"))-len(x.get("voters").get("negative"))
		status,hungry=self.__custom_sort()
		return status,hungry

	# def __sync(self):
	# 	# Syncs memory queue with database
	# 	db = self.get_db()
	# 	db_queue = db.get_playlist()

	# 	queue_ids = [item['id'] for item in self.queue]
	# 	db_ids = [item[0] for item in db_queue]

	# 	for id in db_ids:
	# 		if id not in queue_ids:
				
