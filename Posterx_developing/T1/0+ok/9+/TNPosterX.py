# -*- coding: utf-8 -*-
# TNPosterX.py - Universal Graphics Renderer
# By Enigma2 Developer (2025)
# Fully Standalone - No external dependencies

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from Components.Sources.Event import Event
from Components.Renderer.TNPosterXDownloadThread import download_poster, download_backdrop

import NavigationInstance
import os
import sys
import re

PY3 = sys.version_info[0] == 3

try:
	if PY3:
		from _thread import start_new_thread
	else:
		from thread import start_new_thread
except:
	pass

# --- تحديد مجلد الحفظ ---
def get_media_folder():
	paths = ["/media/hdd", "/media/usb", "/media/mmc", "/tmp"]
	for path in paths:
		folder = f"{path}/Poster_X/"
		if os.path.isdir(path) and os.access(path, os.W_OK):
			try:
				os.makedirs(folder, exist_ok=True)
				return folder
			except:
				continue
	return "/tmp/Poster_X/"

path_folder = get_media_folder()
backdrop_path = os.path.join(path_folder, "backdrop/")
try:
	os.makedirs(backdrop_path, exist_ok=True)
except:
	backdrop_path = path_folder  # fallback

# --- تنظيف النص (مُبسط من Agp_lib.py) ---
def convtext(text):
	if not text or not str(text).strip():
		return ""
	text = str(text).lower().strip()
	# إزالة الأنماط الشائعة
	text = re.sub(r'[\(\[].*?[\)\]]', '', text)
	text = re.sub(r'\s-\s.*', '', text)
	text = re.sub(r'[:!]', '', text)
	text = re.sub(r'\s(odc\.|ep\.|pt\.|parte)\s*\d+', '', text, flags=re.I)
	text = re.sub(r'\s(18\+|16\+|12\+|7\+|6\+|0\+)', '', text)
	text = re.sub(r'\s(HD|FHD|UHD|4K|1080p|720p)', '', text)
	text = re.sub(r'\s(المسلسل العربي|مسلسل|برنامج|فيلم وثائقى|حفل)', '', text)
	text = re.sub(r'[^\w\s]', ' ', text)
	text = re.sub(r'\s+', ' ', text).strip()
	return text.upper()

# --- الرياندر الرئيسي ---
class TNPosterX(Renderer):
	GUI_WIDGET = ePixmap

	def __init__(self):
		Renderer.__init__(self)
		self.type = "poster"
		self.canal = [None] * 3
		self.old_title = ""
		self.timer = eTimer()
		self.timer.callback.append(self.showImage)

	def applySkin(self, desktop, parent):
		for attrib, value in self.skinAttributes:
			if attrib == "type":
				self.type = value.lower()
		return Renderer.applySkin(self, desktop, parent)

	def changed(self, what):
		if not self.instance or what[0] == self.CHANGED_CLEAR:
			self.instance.hide()
			return

		try:
			event = self.source.event
			if not event:
				return

			title = event.getEventName()
			if not title:
				return

			if title == self.old_title:
				return
			self.old_title = title

			# تحديد المسار
			if self.type == "backdrop":
				img_path = os.path.join(backdrop_path, convtext(title) + ".jpg")
			else:
				img_path = os.path.join(path_folder, convtext(title) + ".jpg")

			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(100, True)
			else:
				self.canal[0] = title
				self.canal[1] = event.getShortDescription() or ""
				self.canal[2] = event.getExtendedDescription() or ""
				start_new_thread(self.downloadImage, ())
		except Exception as e:
			self.instance.hide()

	def downloadImage(self):
		try:
			title = self.canal[0]
			if self.type == "backdrop":
				img_path = os.path.join(backdrop_path, convtext(title) + ".jpg")
				if not os.path.exists(img_path):
					download_backdrop(img_path, title, self.canal[1], self.canal[2])
			else:
				img_path = os.path.join(path_folder, convtext(title) + ".jpg")
				if not os.path.exists(img_path):
					download_poster(img_path, title, self.canal[1], self.canal[2])
			self.timer.start(10, True)
		except:
			pass

	def showImage(self):
		title = self.canal[0]
		if self.type == "backdrop":
			img_path = os.path.join(backdrop_path, convtext(title) + ".jpg")
		else:
			img_path = os.path.join(path_folder, convtext(title) + ".jpg")

		if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
			try:
				self.instance.setPixmap(loadJPG(img_path))
				self.instance.setScale(1 if self.type == "backdrop" else 2)
				self.instance.show()
			except:
				self.instance.hide()
		else:
			self.instance.hide()