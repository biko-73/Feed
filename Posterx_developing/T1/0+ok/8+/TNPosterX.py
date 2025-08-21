# -*- coding: utf-8 -*-
# TNPosterX.py - Light & Fast
# By Enigma2 Developer (2025)

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from Components.Sources.Event import Event
from Components.Renderer.TNPosterXDownloadThread import download_poster, download_backdrop

import NavigationInstance
import os
import sys

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
			os.makedirs(folder, exist_ok=True)
			return folder
	return "/tmp/Poster_X/"

path_folder = get_media_folder()
backdrop_path = os.path.join(path_folder, "backdrop/")
os.makedirs(backdrop_path, exist_ok=True)

# --- تنظيف النص ---
def convtext(text):
	if not text or not str(text).strip():
		return ""
	text = str(text).lower().strip()
	# إزالة الأنماط الشائعة
	text = text.replace('live:', '').replace('18+', '').replace('16+', '')
	text = text.replace('720p', '').replace('1080p', '').replace('hd', '')
	text = text.replace('فيلم وثائقى', '').replace('مسلسل', '')
	text = re.sub(r'[\(\[].*?[\)\]]', '', text)
	text = re.sub(r'\s-\s.*', '', text)
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
				img_path = backdrop_path + convtext(title) + ".jpg"
			else:
				img_path = path_folder + convtext(title) + ".jpg"

			if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
				self.timer.start(100, True)
			else:
				self.canal[0] = title
				self.canal[1] = event.getShortDescription() or ""
				self.canal[2] = event.getExtendedDescription() or ""
				start_new_thread(self.downloadImage, ())

		except:
			self.instance.hide()

	def downloadImage(self):
		try:
			title = self.canal[0]
			clean_title = convtext(title)
			if self.type == "backdrop":
				img_path = backdrop_path + clean_title + ".jpg"
				if not os.path.exists(img_path):
					download_backdrop(img_path, title, self.canal[1], self.canal[2])
			else:
				img_path = path_folder + clean_title + ".jpg"
				if not os.path.exists(img_path):
					download_poster(img_path, title, self.canal[1], self.canal[2])
			self.timer.start(10, True)
		except:
			pass

	def showImage(self):
		title = self.canal[0]
		if self.type == "backdrop":
			img_path = backdrop_path + convtext(title) + ".jpg"
		else:
			img_path = path_folder + convtext(title) + ".jpg"

		if os.path.exists(img_path) and os.path.getsize(img_path) > 0:
			self.instance.setPixmap(loadJPG(img_path))
			self.instance.setScale(1 if self.type == "backdrop" else 2)
			self.instance.show()
		else:
			self.instance.hide()