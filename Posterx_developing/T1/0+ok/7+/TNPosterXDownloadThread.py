# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py - Simple & Reliable
# By Enigma2 Developer (2025)

import os
import sys
import re
import requests
import threading
from time import time

PY3 = sys.version_info[0] == 3

try:
	if PY3:
		from urllib.parse import quote
	else:
		from urllib2 import quote
except:
	quote = lambda s: s

# --- مفاتيح API ---
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

# --- حجم الصورة ---
isz = "185,278"  # للبوستر
bsz = "1920,1080"  # للخلفية

# --- User Agent ---
headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
}

# --- استيراد المتغيرات ---
try:
	from Components.Renderer.TNPosterX import pdb, path_folder, convtext
except Exception as e:
	print(f"[TNPosterXDownloadThread] Import error: {str(e)}")
	path_folder = "/tmp/Poster_X/"
	os.makedirs(path_folder, exist_ok=True)

class TNPosterXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		while True:
			try:
				canal = pdb.get()
				title = canal[2]
				shortdesc = canal[3]
				fulldesc = canal[4]
				clean_title = canal[5]

				# تحديد نوع الصورة
				if canal[6] == "backdrop" if len(canal) > 6 else False:
					dwn_file = path_folder + clean_title + "_backdrop.jpg"
					if not os.path.exists(dwn_file):
						val, log = self.search_tmdb_backdrop(dwn_file, title, shortdesc, fulldesc)
				else:
					dwn_file = path_folder + clean_title + ".jpg"
					if not os.path.exists(dwn_file):
						val, log = self.search_tmdb(dwn_file, title, shortdesc, fulldesc)

				if not val:
					print(f"[TNPosterXDownloadThread] Failed to download: {log}")
				pdb.task_done()
			except Exception as e:
				print(f"[TNPosterXDownloadThread] Error in run: {str(e)}")

	def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc):
		try:
			if not title:
				return False, "No title"
			query = quote(title)
			url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language=en"
			resp = requests.get(url, headers=headers, timeout=10).json()
			if resp.get("results"):
				poster_path = resp["results"][0].get("poster_path")
				if poster_path:
					url_poster = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
					return self.savePoster(url_poster, dwn_poster), "TMDB Poster OK"
			return False, "No poster from TMDB"
		except Exception as e:
			if os.path.exists(dwn_poster):
				os.remove(dwn_poster)
			return False, f"TMDB Error: {str(e)}"

	def search_tmdb_backdrop(self, dwn_backdrop, title, shortdesc, fulldesc):
		try:
			if not title:
				return False, "No title"
			query = quote(title)
			url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language=en"
			resp = requests.get(url, headers=headers, timeout=10).json()
			if resp.get("results"):
				movie_id = resp["results"][0].get("id")
				if movie_id:
					url_details = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api}&language=en"
					details = requests.get(url_details, headers=headers, timeout=10).json()
					backdrop_path = details.get("backdrop_path")
					if backdrop_path:
						url_backdrop = f"https://image.tmdb.org/t/p/w{bsz.split(',')[0]}{backdrop_path}"
						return self.savePoster(url_backdrop, dwn_backdrop), "TMDB Backdrop OK"
			return False, "No backdrop from TMDB"
		except Exception as e:
			if os.path.exists(dwn_backdrop):
				os.remove(dwn_backdrop)
			return False, f"TMDB Backdrop Error: {str(e)}"

	def savePoster(self, url, filepath):
		try:
			r = requests.get(url, headers=headers, stream=True, timeout=10, allow_redirects=True)
			if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
				with open(filepath, 'wb') as f:
					for chunk in r.iter_content(1024):
						f.write(chunk)
				return os.path.exists(filepath) and os.path.getsize(filepath) > 0
		except Exception as e:
			print(f"[TNPosterXDownloadThread] Save error: {str(e)}")
		return False

# --- بدء تشغيل الخيط ---
threadDB = TNPosterXDownloadThread()
threadDB.start()