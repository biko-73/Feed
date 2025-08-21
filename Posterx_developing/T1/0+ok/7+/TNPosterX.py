# -*- coding: utf-8 -*-
# TNPosterX.py - Universal Graphics Renderer
# Based on working version by digiteng, sunriser, beber
# Fixed & Optimized by Enigma2 Developer (2025)

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG, eEPGCache
from ServiceReference import ServiceReference
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

# --- تحديد اللغة ---
try:
	from Components.config import config
	lng = config.osd.language.value[:2]
except:
	lng = "en"

# --- تحديد مجلد الحفظ ---
def get_media_folder():
	paths = ["/media/hdd", "/media/usb", "/media/mmc", "/tmp"]
	for path in paths:
		if os.path.isdir(path) and os.access(path, os.W_OK):
			folder = f"{path}/Poster_X/"
			os.makedirs(folder, exist_ok=True)
			return folder
	return "/tmp/Poster_X/"

path_folder = get_media_folder()

# --- تنظيف النص ---
def convtext(text):
	if not text or not str(text).strip():
		return ""
	text = str(text).lower().strip()
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
	# إزالة الأنماط الشائعة
	text = re.sub(r'[\(\[].*?[\)\]]', '', text)
	text = re.sub(r'\s-\s.*', '', text)
	text = re.sub(r'[:!]', '', text)
	text = re.sub(r'\s(odc\.|ep\.|pt\.|parte)\s*\d+', '', text, flags=re.I)
	text = re.sub(r'\s(18\+|16\+|12\+|7\+|6\+|0\+)', '', text)
	text = re.sub(r'\s(HD|FHD|UHD|4K|1080p|720p)', '', text)
	text = re.sub(r'\s(المسلسل العربي|مسلسل|برنامج|فيلم وثائقى|حفل)', '', text)
	text = re.sub(r'\s+', ' ', text).strip()
	return text.upper()

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
		self.type = "poster"
		self.canal = [None] * 6
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
		try:
			if isinstance(self.source, Event):
				if self.nxts:
					service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
				else:
					self.canal[1] = self.source.event.getBeginTime()
					self.canal[2] = self.source.event.getEventName() or ""
					self.canal[3] = self.source.event.getExtendedDescription() or ""
					self.canal[4] = self.source.event.getShortDescription() or ""
					self.canal[5] = convtext(self.canal[2])
			elif hasattr(self.source, "getCurrentService"):
				service = self.source.getCurrentService()

			if service:
				events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
				if len(events) > self.nxts:
					self.canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
					self.canal[1] = events[self.nxts][1]
					self.canal[2] = events[self.nxts][4] or ""
					self.canal[3] = events[self.nxts][5] or ""
					self.canal[4] = events[self.nxts][6] or ""
					self.canal[5] = convtext(self.canal[2])

			curCanal = "{}-{}-{}".format(self.canal[1], self.canal[5], self.type)
			if curCanal == self.oldCanal:
				return
			self.oldCanal = curCanal

			# تحديد المسار
			img_path = path_folder + self.canal[5] + ("_backdrop.jpg" if self.type == "backdrop" else ".jpg")

			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(100, True)
			else:
				pdb.put(self.canal[:])
				start_new_thread(self.waitImage, ())

		except Exception as e:
			self.instance.hide()

	def showImage(self):
		img_path = path_folder + self.canal[5] + ("_backdrop.jpg" if self.type == "backdrop" else ".jpg")
		if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
			self.instance.setPixmap(loadJPG(img_path))
			self.instance.setScale(1 if self.type == "backdrop" else 2)
			self.instance.show()
		else:
			self.instance.hide()

	def waitImage(self):
		img_path = path_folder + self.canal[5] + ("_backdrop.jpg" if self.type == "backdrop" else ".jpg")
		for _ in range(180):
			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(10, True)
				return
			time.sleep(0.5)
		self.instance.hide()