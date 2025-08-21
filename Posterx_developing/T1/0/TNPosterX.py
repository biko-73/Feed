# -*- coding: utf-8 -*-
# TNPosterX - Advanced Poster Renderer
# Based on digiteng, beber, Lululla (AGP)
# Optimized & Standalone - No external plugin required
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
	lng = config.osd.language.value[:2]  # "en", "ar", "fr"
except:
	lng = "en"

apdb = {}

# --- تحديد مجلد الحفظ (مُحسّن من Agp_Utils.py) ---
def get_media_folder():
	paths = ["/media/hdd", "/media/usb", "/media/mmc", "/tmp"]
	for path in paths:
		folder = f"{path}/Poster_X/"
		if os.path.isdir(path) and os.access(path, os.W_OK):
			os.makedirs(folder, exist_ok=True)
			return folder
	return "/tmp/Poster_X/"

path_folder = get_media_folder()

# --- تنظيف النص (مُحسّن من Agp_lib.py) ---
REGEX = re.compile(
	r'[\(\[].*?[\)\]]|'
	r':?\s?odc\.\d+|'
	r'\d+\s?:?\s?odc\.\d+|'
	r'[:!]|'
	r'\s-\s.*|'
	r',|'
	r'/.*|'
	r'\|\s?\d+\+|'
	r'\d+\+|'
	r'\s\*\d{4}\Z|'
	r'[\(\[\|].*?[\)\]\|]|'
	r'(?:\"[\.|\,]?\s.*|\"|\.\s.+)|'
	r'Премьера\.\s|'
	r'[хмтдХМТД]/[фс]\s|'
	r'\s[сС](?:езон|ерия|-н|-я)\s.*|'
	r'\s\d{1,3}\s[чсЧС]\.?\s.*|'
	r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'
	r'\s[чсЧС]\.?\s\d{1,3}.*|'
	r'\d{1,3}-(?:я|й)\s?с-н.*', re.DOTALL)

CHAR_REPLACEMENTS = {
	"live:": "", "18+": "", "16+": "", "12+": "", "7+": "", "6+": "", "0+": "",
	"المسلسل العربي": "", "مسلسل": "", "برنامج": "", "فيلم وثائقى": "", "حفل": "",
	"HD": "", "FHD": "", "UHD": "", "4K": "", "1080p": "", "720p": ""
}

def convtext(text):
	if not text or not str(text).strip():
		return ""
	text = str(text).lower().strip()
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
	text = REGEX.sub('', text)
	for char, repl in CHAR_REPLACEMENTS.items():
		text = text.replace(char, repl)
	text = re.sub(r'\s+', ' ', text).strip()
	return text.upper()

# --- صف الانتظار ---
if PY3:
	pdb = queue.LifoQueue()
else:
	pdb = Queue.LifoQueue()

# --- خيط التنزيل ---
class PosterDB(TNPosterXDownloadThread):
	def __init__(self):
		TNPosterXDownloadThread.__init__(self)

	def run(self):
		while True:
			canal = pdb.get()
			dwn_poster = path_folder + canal[5] + ".jpg"
			if os.path.exists(dwn_poster):
				os.utime(dwn_poster, (time.time(), time.time()))
			else:
				val, log = self.search_tmdb(dwn_poster, canal[2], canal[4], canal[3], canal[0])
				if not val and lng == "fr":
					val, log = self.search_molotov_google(dwn_poster, canal[2], canal[4], canal[3], canal[0])
				if not val:
					val, log = self.search_google(dwn_poster, canal[2], canal[4], canal[3], canal[0])
			pdb.task_done()

threadDB = PosterDB()
threadDB.start()

# --- الرياندر الرئيسي ---
class TNPosterX(Renderer):
	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.nxts = 0
		self.canal = [None]*6
		self.oldCanal = None
		self.timer = eTimer()
		self.timer.callback.append(self.showPoster)

	def applySkin(self, desktop, parent):
		for attrib, value in self.skinAttributes:
			if attrib == "nexts":
				self.nxts = int(value)
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
					if self.canal[0] not in apdb:
						apdb[self.canal[0]] = service.toString()

			if not servicetype:
				self.instance.hide()
				return

			curCanal = "{}-{}".format(self.canal[1], self.canal[2])
			if curCanal == self.oldCanal:
				return
			self.oldCanal = curCanal

			pstrNm = path_folder + self.canal[5] + ".jpg"
			if os.path.exists(pstrNm):
				self.timer.start(100, True)
			else:
				pdb.put(self.canal[:])
				start_new_thread(self.waitPoster, ())

		except Exception as e:
			self.instance.hide()

	def showPoster(self):
		pstrNm = path_folder + self.canal[5] + ".jpg"
		if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
			self.instance.setPixmap(loadJPG(pstrNm))
			self.instance.setScale(2)
			self.instance.show()
		else:
			self.instance.hide()

	def waitPoster(self):
		pstrNm = path_folder + self.canal[5] + ".jpg"
		for _ in range(180):
			if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
				self.timer.start(10, True)
				return
			time.sleep(0.5)
		self.instance.hide()