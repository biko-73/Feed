# -*- coding: utf-8 -*-
# PosterX - Automatic Poster Renderer for Enigma2
# by digiteng, sunriser, beber
# Modified & Fixed by Enigma2 Developer (2025)
# Stage 2: Add Backdrop Support - FIXED

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

# تحديد اللغة
try:
	from Components.config import config
	lng = config.osd.language.value  # مثل: "en_EN", "fr_FR"
except:
	lng = "en_EN"

# قاعدة بيانات القنوات التلقائية
apdb = {}

# --- إعدادات القائمة التلقائية ---
autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'  # غيّر حسب الحاجة
autobouquet_count = 32  # عدد العناصر للبحث التلقائي

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

# تحديد مجلد الحفظ
path_folder = "/media/hdd/Poster_X/"
if not os.path.isdir(path_folder):
	path_folder = "/media/usb/Poster_X/"
if not os.path.isdir(path_folder):
	path_folder = "/tmp/Poster_X/"
os.makedirs(path_folder, exist_ok=True)

# إنشاء مجلد الباكدروب
backdrop_path = os.path.join(path_folder, "backdrop/")
os.makedirs(backdrop_path, exist_ok=True)

# تنظيف اسم الفيلم
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
	r'(х|Х|м|М|т|т|д|д)/с\s|'
	r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
	r'\s\d{1,3}\s[чсЧС]\.?\s.*|'
	r'\.\s\d{1,3}\s[чсЧС]\.?\s.*|'
	r'\s[чсЧС]\.?\s\d{1,3}.*|'
	r'\d{1,3}-(?:я|й)\s?с-н.*|', re.DOTALL)

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

# إنشاء صف الانتظار
if PY3:
	pdb = queue.LifoQueue()
else:
	pdb = Queue.LifoQueue()

# --- الرياندر الرئيسي ---
class TNPosterX(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.nxts = 0
		self.type = "poster"  # الافتراضي
		self.canal = [None] * 6
		self.oldCanal = ""  # بدأ فارغًا
		self.timer = eTimer()
		self.timer.callback.append(self.showPoster)

	GUI_WIDGET = ePixmap

	def applySkin(self, desktop, parent):
		for attrib, value in self.skinAttributes:
			if attrib == "nexts":
				self.nxts = int(value)
			elif attrib == "type":
				self.type = value.lower()  # دعم type="backdrop"
		return Renderer.applySkin(self, desktop, parent)

	def changed(self, what):
		if not self.instance:
			return
		if what[0] == self.CHANGED_CLEAR:
			self.instance.hide()
			return

		servicetype = None
		service = None
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
					self.canal[0] = None
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

			# معرفة فريدة لكل حدث ونوع
			curCanal = "{}-{}-{}".format(self.canal[1], self.canal[5], self.type)

			# إذا لم تتغير، لا نفعل شيئًا
			if curCanal == self.oldCanal:
				return

			# تحديث المعرف القديم
			self.oldCanal = curCanal

			# إخفاء الصورة فورًا عند تغيير الحدث
			self.instance.hide()

			# تحديد المسار حسب النوع
			if self.type == "backdrop":
				pstrNm = backdrop_path + self.canal[5] + ".jpg"
			else:
				pstrNm = path_folder + self.canal[5] + ".jpg"

			if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
				self.timer.start(100, True)
			else:
				pdb.put(self.canal[:])
				start_new_thread(self.waitPoster, ())

		except Exception as e:
			self.instance.hide()

	def showPoster(self):
		# تحديد المسار حسب النوع
		if self.type == "backdrop":
			pstrNm = backdrop_path + self.canal[5] + ".jpg"
		else:
			pstrNm = path_folder + self.canal[5] + ".jpg"

		if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
			self.instance.setPixmap(loadJPG(pstrNm))
			self.instance.setScale(1 if self.type == "backdrop" else 2)
			self.instance.show()
		else:
			self.instance.hide()

	def waitPoster(self):
		# تحديد المسار حسب النوع
		if self.type == "backdrop":
			pstrNm = backdrop_path + self.canal[5] + ".jpg"
		else:
			pstrNm = path_folder + self.canal[5] + ".jpg"

		for _ in range(180):
			if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
				self.timer.start(10, True)
				return
			time.sleep(0.5)
		self.instance.hide()