# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py - Stage 1: Add Backdrop Support

import os
import sys
import re
import requests
import threading
from configparser import ConfigParser

PY3 = sys.version_info[0] == 3

try:
	if PY3:
		from urllib.parse import quote
	else:
		from urllib2 import quote
except:
	quote = lambda s: s

try:
	from Components.Language import language
	lang = language.getLanguage()[:2]
except:
	lang = "en"

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
# --- حجم الصورة ---
isz = "185,278"  # للبوستر
bsz = "1920,1080"  # للخلفية

class TNPosterXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def search_tmdb(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			fd = "{}\n{}\n{}".format(title, shortdesc or "", fulldesc or "")
			srch = "multi"
			year = None
			try:
				year_match = re.search(r'\b(19|20)\d{2}\b', fd)
				year = year_match.group(0) if year_match else None
			except:
				pass
			if any(word in fd.lower() for word in ["film", "movie", "фильм", "кино", "cinema"]):
				srch = "movie"
			elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
				srch = "tv"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/{srch}?api_key={tmdb_api}&query={query}"
			if year:
				url_tmdb += f"&year={year}"
			url_tmdb += f"&language={lang}"
			resp = requests.get(url_tmdb, timeout=10).json()
			if resp.get("results"):
				poster_path = resp["results"][0].get("poster_path")
				if poster_path:
					url_poster = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
					self.savePoster(dwn_poster, url_poster)
					return True, f"[TMDB OK] {title}"
			return False, "[TMDB] No result"
		except Exception as e:
			if os.path.exists(dwn_poster):
				os.remove(dwn_poster)
			return False, f"[TMDB Error] {str(e)}"

	def search_tmdb_backdrop(self, dwn_backdrop, title, shortdesc, fulldesc, channel=None):
		try:
			if not title:
				return False, "No title"
			fd = "{}\n{}\n{}".format(title, shortdesc or "", fulldesc or "")
			srch = "multi"
			year = None
			try:
				year_match = re.search(r'\b(19|20)\d{2}\b', fd)
				year = year_match.group(0) if year_match else None
			except:
				pass
			if any(word in fd.lower() for word in ["film", "movie", "фильم", "кино", "cinema"]):
				srch = "movie"
			elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
				srch = "tv"
			query = quote(title)
			url_tmdb = f"https://api.themoviedb.org/3/search/{srch}?api_key={tmdb_api}&query={query}"
			if year:
				url_tmdb += f"&year={year}"
			url_tmdb += f"&language={lang}"
			resp = requests.get(url_tmdb, timeout=10).json()
			if resp.get("results"):
				backdrop_path = resp["results"][0].get("backdrop_path")
				if backdrop_path:
					url_backdrop = f"https://image.tmdb.org/t/p/w{bsz.split(',')[0]}{backdrop_path}"
					self.savePoster(dwn_backdrop, url_backdrop)
					return True, f"[TMDB Backdrop OK] {title}"
			return False, "[TMDB Backdrop] No result"
		except Exception as e:
			if os.path.exists(dwn_backdrop):
				os.remove(dwn_backdrop)
			return False, f"[TMDB Backdrop Error] {str(e)}"

	def search_molotov_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			if "fr" not in lang.lower():
				return False, "Not FR"
			headers = {"User-Agent": "Mozilla/5.0"}
			query = f"site:molotov.tv {quote(title)}"
			url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=ift:jpg,isz:m"
			resp = requests.get(url, headers=headers, timeout=10).text
			match = re.search(r'\],\["https://([^"]+)",\d+,\d+]', resp)
			if match and "molotov" in match.group(1):
				url_poster = "https://" + match.group(1)
				self.savePoster(dwn_poster, url_poster)
				return True, f"[Molotov OK] {title}"
			return False, "[Molotov] Not found"
		except:
			return False, "[Molotov Error]"

	def search_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
		try:
			headers = {"User-Agent": "Mozilla/5.0"}
			query = quote(title)
			url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=ift:jpg,isz:m"
			resp = requests.get(url, headers=headers, timeout=10).text
			match = re.search(r'\],\["https://([^"]+)",\d+,\d+]', resp)
			if match:
				url_poster = "https://" + match.group(1)
				self.savePoster(dwn_poster, url_poster)
				return True, f"[Google OK] {title}"
			return False, "[Google] Not found"
		except:
			return False, "[Google Error]"

	def savePoster(self, dwn_poster, url_poster):
		try:
			r = requests.get(url_poster, stream=True, timeout=10, allow_redirects=True)
			if r.status_code == 200:
				with open(dwn_poster, 'wb') as f:
					for chunk in r.iter_content(1024):
						f.write(chunk)
		except:
			pass