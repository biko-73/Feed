# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py
# Universal Graphics Downloader for TNPosterX
# By Enigma2 Developer (2025)

import os
import sys
import re
import requests
import threading
from time import time
from random import choice

PY3 = sys.version_info[0] == 3

try:
	if PY3:
		from urllib.parse import quote
	else:
		from urllib2 import quote
except:
	quote = lambda s: s

# --- اللغة ---
try:
	from Components.Language import language
	lang = language.getLanguage()[:2]
except:
	lang = "en"

# --- مفاتيح API ---
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

# --- حجم الصورة ---
isz = "185,278"
bsz = "1920,1080"
bnz = "1920,300"
lsz = "500,281"

# --- User Agents ---
AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edge/87.0.664.75"
]
headers = {"User-Agent": choice(AGENTS)}

# --- استيراد المتغيرات من TNPosterX ---
try:
	from Components.Renderer.TNPosterX import poster_path, backdrop_path, banner_path, logo_path, convtext, apdb
except Exception as e:
	print(f"[TNPosterXDownloadThread] Error importing from TNPosterX: {str(e)}")
	# تعريف افتراضي
	poster_path = "/tmp/TNPosterX/poster/"
	backdrop_path = "/tmp/TNPosterX/backdrop/"
	banner_path = "/tmp/TNPosterX/banner/"
	logo_path = "/tmp/TNPosterX/logo/"

# --- خيط التنزيل ---
class TNPosterXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		while True:
			canal = pdb.get()
			if canal[6] == "backdrop":
				dwn_file = backdrop_path + canal[5] + ".jpg"
			elif canal[6] == "banner":
				dwn_file = banner_path + canal[5] + ".jpg"
			elif canal[6] == "logo":
				dwn_file = logo_path + canal[5] + ".png"
			else:
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
				else:
					val, log = self.search_tmdb(dwn_file, canal[2], canal[4], canal[3], canal[0])
				
				if not val and lng == "fr":
					val, log = self.search_molotov_google(dwn_file, canal[2], canal[4], canal[3], canal[0])
				if not val:
					val, log = self.search_google(dwn_file, canal[2], canal[4], canal[3], canal[0])
			pdb.task_done()

	def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			fd = f"{title}\n{shortdesc or ''}\n{fulldesc or ''}"
			srch = "multi"
			year = None
			year_match = re.search(r'\b(19|20)\d{2}\b', fd)
			year = year_match.group(0) if year_match else None
			if any(word in fd.lower() for word in ["film", "movie", "фильм", "кино", "cinema"]):
				srch = "movie"
			elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
				srch = "tv"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/{srch}?api_key={tmdb_api}&query={query}"
			if year and srch == "movie":
				url_tmdb += f"&year={year}"
			url_tmdb += f"&language={lang}"
			resp = requests.get(url_tmdb, headers=headers, timeout=10).json()
			if resp.get("results"):
				poster_path = resp["results"][0].get("poster_path")
				if poster_path:
					url_poster = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
					if self.savePoster(url_poster, dwn_poster):
						return True, f"[SUCCESS] TMDB Poster: {title}"
			return False, "No poster from TMDB"
		except Exception as e:
			if os.path.exists(dwn_poster):
				os.remove(dwn_poster)
			return False, f"TMDB Poster error: {str(e)}"

	def search_tmdb_backdrop(self, dwn_backdrop, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			fd = f"{title}\n{shortdesc or ''}\n{fulldesc or ''}"
			srch = "multi"
			year = None
			year_match = re.search(r'\b(19|20)\d{2}\b', fd)
			year = year_match.group(0) if year_match else None
			if any(word in fd.lower() for word in ["film", "movie", "фильм", "кино", "cinema"]):
				srch = "movie"
			elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
				srch = "tv"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/{srch}?api_key={tmdb_api}&query={query}"
			if year and srch == "movie":
				url_tmdb += f"&year={year}"
			url_tmdb += f"&language={lang}"
			resp = requests.get(url_tmdb, headers=headers, timeout=10).json()
			if resp.get("results"):
				backdrop_path = resp["results"][0].get("backdrop_path")
				if backdrop_path:
					url_backdrop = f"https://image.tmdb.org/t/p/w{bsz.split(',')[0]}{backdrop_path}"
					if self.savePoster(url_backdrop, dwn_backdrop):
						return True, f"[SUCCESS] TMDB Backdrop: {title}"
			return False, "No backdrop from TMDB"
		except Exception as e:
			if os.path.exists(dwn_backdrop):
				os.remove(dwn_backdrop)
			return False, f"TMDB Backdrop error: {str(e)}"

	def search_tmdb_banner(self, dwn_banner, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
			resp = requests.get(url_tmdb, headers=headers, timeout=10).json()
			if resp.get("results"):
				movie_id = resp["results"][0].get("id")
				if movie_id:
					url_still = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={tmdb_api}"
					still_resp = requests.get(url_still, headers=headers, timeout=10).json()
					if still_resp.get("posters"):
						for poster in still_resp["posters"]:
							if poster.get("aspect_ratio") and poster["aspect_ratio"] > 1.5:
								url_banner = f"https://image.tmdb.org/t/p/w{bnz.split(',')[0]}{poster['file_path']}"
								if self.savePoster(url_banner, dwn_banner):
									return True, f"[SUCCESS] TMDB Banner: {title}"
			return False, "No banner from TMDB"
		except Exception as e:
			if os.path.exists(dwn_banner):
				os.remove(dwn_banner)
			return False, f"TMDB Banner error: {str(e)}"

	def search_tmdb_logo(self, dwn_logo, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
			resp = requests.get(url_tmdb, headers=headers, timeout=10).json()
			if resp.get("results"):
				movie_id = resp["results"][0].get("id")
				if movie_id:
					url_logo = f"https://api.themoviedb.org/3/movie/{movie_id}/images?api_key={tmdb_api}&include_image_language=en,null"
					logo_resp = requests.get(url_logo, headers=headers, timeout=10).json()
					if logo_resp.get("logos"):
						for logo in logo_resp["logos"]:
							if logo.get("file_type") == "png" and logo.get("aspect_ratio") == 0.5:
								url_logo = f"https://image.tmdb.org/t/p/w{lsz.split(',')[0]}{logo['file_path']}"
								if self.savePoster(url_logo, dwn_logo):
									return True, f"[SUCCESS] TMDB Logo: {title}"
			return False, "No logo from TMDB"
		except Exception as e:
			if os.path.exists(dwn_logo):
				os.remove(dwn_logo)
			return False, f"TMDB Logo error: {str(e)}"

	def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			if "fr" not in lang:
				return False, "Not FR"
			query = f"site:molotov.tv {quote(title)}"
			if channel and title.lower().find(channel.split()[0].lower()) < 0:
				query += f" {quote(channel)}"
			url = f"https://www.google.com/search?q={query}&tbm=isch"
			resp = requests.get(url, headers=headers, cookies={'CONSENT': 'YES+'}, timeout=10).text
			match = re.search(r'\],\["https://(.*?)",\d+,\d+]', resp)
			if match and "molotov" in match.group(1):
				url_poster = "https://" + match.group(1)
				if self.savePoster(url_poster, dwn_poster):
					return True, f"[SUCCESS] Molotov: {title}"
			return False, "No poster from Molotov"
		except Exception as e:
			return False, f"Molotov error: {str(e)}"

	def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			query = f'"{quote(title)}"'
			if channel and title.lower().find(channel.lower()) < 0:
				query += f" {quote(channel)}"
			url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=sbd:0"
			resp = requests.get(url, headers=headers, cookies={'CONSENT': 'YES+'}, timeout=10).text
			match = re.search(r'\],\["https://(.*?)",\d+,\d+]', resp)
			if match:
				url_poster = "https://" + match.group(1)
				if self.savePoster(url_poster, dwn_poster):
					return True, f"[SUCCESS] Google: {title}"
			return False, "No poster from Google"
		except Exception as e:
			return False, f"Google error: {str(e)}"

	def savePoster(self, url, filepath):
		try:
			if os.path.exists(filepath):
				if os.path.getsize(filepath) > 1024:
					return True
				else:
					os.remove(filepath)
			r = requests.get(url, headers=headers, stream=True, timeout=10, allow_redirects=True)
			if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
				with open(filepath, 'wb') as f:
					for chunk in r.iter_content(1024):
						f.write(chunk)
				return os.path.exists(filepath) and os.path.getsize(filepath) > 0
		except:
			pass
		return False

# --- استيراد pdb من TNPosterX ---
try:
	from Components.Renderer.TNPosterX import pdb
except Exception as e:
	print(f"[TNPosterXDownloadThread] Error importing pdb: {str(e)}")
	if PY3:
		import queue
		pdb = queue.LifoQueue()
	else:
		import Queue
		pdb = Queue.LifoQueue()

# --- بدء تشغيل الخيط ---
threadDB = TNPosterXDownloadThread()
threadDB.daemon = True
threadDB.start()

# --- تنظيف تلقائي ---
def auto_clean_thread():
	while True:
		time.sleep(7200)
		try:
			from Components.Renderer.TNPosterX import poster_path, backdrop_path, banner_path, logo_path
			now = time()
			for folder in [poster_path, backdrop_path, banner_path, logo_path]:
				for f in os.listdir(folder):
					fp = os.path.join(folder, f)
					if os.path.isfile(fp) and (now - os.path.getmtime(fp)) > 259200:
						os.remove(fp)
		except:
			pass

threading.Thread(target=auto_clean_thread, daemon=True).start()