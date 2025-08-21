# -*- coding: utf-8 -*-
# TNPosterX.py - Stage 1: Add Backdrop Support
# Based on working version by digiteng, sunriser, beber
# By Enigma2 Developer (2025)

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG, eEPGCache
from ServiceReference import ServiceReference
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.Sources.EventInfo import EventInfo
from Components.Sources.Event import Event
from Components.Renderer.TNPosterXDownloadThread import TNPosterXDownloadThread

import NavigationInstance
import os
import sys
import re
import time
import socket
import unicodedata

PY3 = sys.version_info[0] == 3

try:
	if PY3:
		import queue
		from _thread import start_new_thread
	else:
		import Queue
		from thread import start_new_thread
except:
	pass

epgcache = eEPGCache.getInstance()

try:
	from Components.config import config
	lng = config.osd.language.value
except:
	lng = "en_EN"

apdb = {}

autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'
autobouquet_count = 32

if os.path.exists(autobouquet_file):
	try:
		with open(autobouquet_file, 'r') as f:
			lines = f.readlines()
		if autobouquet_count > len(lines):
			autobouquet_count = len(lines)
		for i in range(autobouquet_count):
			if '#SERVICE' in lines[i]:
				line = lines[i][9:].strip().split(':')
				if len(line) == 11:
					value = ':'.join((line[3], line[4], line[5], line[6]))
					if value != '0:0:0:0':
						service = ':'.join(line[:11])
						apdb[i] = service
	except:
		pass

# --- تحديد مجلدات الحفظ ---
base_path = "/media/hdd/Poster_X/"
if not os.path.isdir(base_path):
	base_path = "/media/usb/Poster_X/"
if not os.path.isdir(base_path):
	base_path = "/tmp/Poster_X/"

# --- إنشاء المجلدات ---
poster_path = os.path.join(base_path, "poster/")
backdrop_path = os.path.join(base_path, "backdrop/")
os.makedirs(poster_path, exist_ok=True)
os.makedirs(backdrop_path, exist_ok=True)

# --- تنظيف النص ---
REGEX = re.compile(
	r'([\(\[]).*?([\)\]])|'
	r'(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|'
	r'( -(.*?).*)|(,)|!|/.*|'
	r'\|\s[0-9]+\+|[0-9]+\+|'
	r'\s\d{4}\Z|'
	r'([\(\[\|].*?[\)\]\|])|'
	r'(\"|\"\.|\"\,|\.)\s.+|'
	r'\"|:|'
	r'Премьера\.\s|'
	r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
	r'(х|Х|м|М|ت|ت|د|د)/س\s|'
	r'\s(س|س)(езон|يريا|-ن|-ي)\s.+|'
	r'\s\d{1,3}\s(س|س\.|د\.|د)\s.+|'
	r'\.\s\d{1,3}\s(س|س\.|د\.|د)\s.+|'
	r'\s(س|س\.|د\.|د)\s\d{1,3}.+|'
	r'\d{1,3}(-ي|-ي|\sس-ن).+|', re.DOTALL)

def convtext(text):
	if not text:
		return ""
	text = REGEX.sub('', text).strip().replace('\xc2\x86', '').replace('\xc2\x87', '')
	try:
		text = str(text, 'utf-8')
	except (TypeError, ValueError):
		pass
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
	return text.upper().strip()

# --- صف الانتظار ---
if PY3:
	pdb = queue.LifoQueue()
else:
	pdb = Queue.LifoQueue()

# --- الرياندر الرئيسي ---
class TNPosterX(Renderer):
	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.nxts = 0
		self.type = "poster"  # الافتراضي
		self.canal = [None]*6
		self.oldCanal = None
		self.timer = eTimer()
		self.timer.callback.append(self.showImage)

	def applySkin(self, desktop, parent):
		for attrib, value in self.skinAttributes:
			if attrib == "nexts":
				self.nxts = int(value)
			elif attrib == "type":
				self.type = value.lower()
		return Renderer.applySkin(self, desktop, parent)

	def changed(self, what):
		if not self.instance or what[0] == self.CHANGED_CLEAR:
			self.instance.hide()
			return

		service = None
		servicetype = None
		try:
			if isinstance(self.source, ServiceEvent):
				service = self.source.getCurrentService()
				servicetype = "ServiceEvent"
			elif isinstance(self.source, CurrentService):
				service = self.source.getCurrentServiceRef()
				servicetype = "CurrentService"
			elif isinstance(self.source, EventInfo):
				service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				servicetype = "EventInfo"
			elif isinstance(self.source, Event):
				if self.nxts:
					service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				else:
					self.canal[1] = self.source.event.getBeginTime()
					self.canal[2] = self.source.event.getEventName() or ""
					self.canal[3] = self.source.event.getExtendedDescription() or ""
					self.canal[4] = self.source.event.getShortDescription() or ""
					self.canal[5] = convtext(self.canal[2])
				servicetype = "Event"

			if service:
				events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
				if len(events) > self.nxts:
					self.canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
					self.canal[1] = events[self.nxts][1]
					self.canal[2] = events[self.nxts][4] or ""
					self.canal[3] = events[self.nxts][5] or ""
					self.canal[4] = events[self.nxts][6] or ""
					self.canal[5] = convtext(self.canal[2])
					if not autobouquet_file and self.canal[0] not in apdb:
						apdb[self.canal[0]] = service.toString()

			if not servicetype:
				self.instance.hide()
				return

			curCanal = "{}-{}-{}".format(self.canal[1], self.canal[2], self.type)
			if curCanal == self.oldCanal:
				return
			self.oldCanal = curCanal

			# تحديد المسار حسب النوع
			if self.type == "backdrop":
				img_path = backdrop_path + self.canal[5] + ".jpg"
			else:
				img_path = poster_path + self.canal[5] + ".jpg"

			if os.path.exists(img_path):
				self.timer.start(100, True)
			else:
				pdb.put(self.canal[:])
				start_new_thread(self.waitImage, ())

		except Exception as e:
			self.instance.hide()

	def showImage(self):
		# تحديد المسار حسب النوع
		if self.type == "backdrop":
			img_path = backdrop_path + self.canal[5] + ".jpg"
		else:
			img_path = poster_path + self.canal[5] + ".jpg"

		if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
			self.instance.setPixmap(loadJPG(img_path))
			self.instance.setScale(1 if self.type == "backdrop" else 2)
			self.instance.show()
		else:
			self.instance.hide()

	def waitImage(self):
		# تحديد المسار حسب النوع
		if self.type == "backdrop":
			img_path = backdrop_path + self.canal[5] + ".jpg"
		else:
			img_path = poster_path + self.canal[5] + ".jpg"

		for _ in range(180):
			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(10, True)
				return
			time.sleep(0.5)
		self.instance.hide()