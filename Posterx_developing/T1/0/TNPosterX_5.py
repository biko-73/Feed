# -*- coding: utf-8 -*-
# TNPosterX - Multi-Type Graphics Renderer
# By Enigma2 Developer (2025)
# Fully Standalone - No external plugin required

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG, loadPNG, eEPGCache
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
	lng = config.osd.language.value[:2]
except:
	lng = "en"

apdb = {}

# --- تحديد مجلدات الحفظ ---
def get_media_folder():
	paths = ["/media/hdd", "/media/usb", "/media/mmc", "/tmp"]
	for path in paths:
		if os.path.isdir(path) and os.access(path, os.W_OK):
			base_folder = f"{path}/Poster_X/"
			os.makedirs(base_folder, exist_ok=True)
			return base_folder
	return "/tmp/Poster_X/"

base_path = get_media_folder()
poster_path = os.path.join(base_path, "poster/")
backdrop_path = os.path.join(base_path, "backdrop/")
banner_path = os.path.join(base_path, "banner/")
logo_path = os.path.join(base_path, "logo/")
os.makedirs(poster_path, exist_ok=True)
os.makedirs(backdrop_path, exist_ok=True)
os.makedirs(banner_path, exist_ok=True)
os.makedirs(logo_path, exist_ok=True)

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
	"HD": "", "FHD": "", "UHD", "4K": "", "1080p": "", "720p": ""
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
			# تحديد المسار حسب النوع
			if canal[6] == "backdrop":
				dwn_file = backdrop_path + canal[5] + ".jpg"
			elif canal[6] == "banner":
				dwn_file = banner_path + canal[5] + ".jpg"
			elif canal[6] == "logo":
				dwn_file = logo_path + canal[5] + ".png"
			else:  # poster
				dwn_file = poster_path + canal[5] + ".jpg"
				
			if os.path.exists(dwn_file):
				os.utime(dwn_file, (time.time(), time.time()))
			else:
				if canal[6] == "backdrop":
					val, log = self.search_tmdb_backdrop(dwn_file, canal[2], canal[4], canal[3], canal[0])
				elif canal[6] == "banner":
					val, log = self.search_tmdb_banner(dwn_file, canal[2], canal[4], canal[3], canal[0])
				elif canal[6] == "logo":
					val, log = self.search_tmdb_logo(dwn_file, canal[2], canal[4], canal[3], canal[0])
				else:  # poster
					val, log = self.search_tmdb(dwn_file, canal[2], canal[4], canal[3], canal[0])
				
				if not val and lng == "fr":
					val, log = self.search_molotov_google(dwn_file, canal[2], canal[4], canal[3], canal[0])
				if not val:
					val, log = self.search_google(dwn_file, canal[2], canal[4], canal[3], canal[0])
			pdb.task_done()

threadDB = PosterDB()
threadDB.start()

# --- الرياندر الرئيسي ---
class TNPosterX(Renderer):
	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.nxts = 0
		self.type = "poster"  # الافتراضي
		self.canal = [None]*7  # أضفنا حقلًا للنوع
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
					self.canal[6] = self.type  # حفظ النوع
					if self.canal[0] not in apdb:
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
			elif self.type == "banner":
				img_path = banner_path + self.canal[5] + ".jpg"
			elif self.type == "logo":
				img_path = logo_path + self.canal[5] + ".png"
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
		elif self.type == "banner":
			img_path = banner_path + self.canal[5] + ".jpg"
		elif self.type == "logo":
			img_path = logo_path + self.canal[5] + ".png"
		else:
			img_path = poster_path + self.canal[5] + ".jpg"

		if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
			if self.type == "logo":
				self.instance.setPixmap(loadPNG(img_path))
			else:
				self.instance.setPixmap(loadJPG(img_path))
			self.instance.setScale(1 if self.type in ["backdrop", "logo"] else 2)
			self.instance.show()
		else:
			self.instance.hide()

	def waitImage(self):
		# تحديد المسار حسب النوع
		if self.type == "backdrop":
			img_path = backdrop_path + self.canal[5] + ".jpg"
		elif self.type == "banner":
			img_path = banner_path + self.canal[5] + ".jpg"
		elif self.type == "logo":
			img_path = logo_path + self.canal[5] + ".png"
		else:
			img_path = poster_path + self.canal[5] + ".jpg"

		for _ in range(180):
			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(10, True)
				return
			time.sleep(0.5)
		self.instance.hide()