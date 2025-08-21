# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py
# Poster & Backdrop Downloader
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
isz = "185,278"  # للبوستر
bsz = "1920,1080"  # للخلفية

# --- User Agents ---
AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
	"Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edge/87.0.664.75"
]
headers = {"User-Agent": choice(AGENTS)}

class TNPosterXDownloadThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

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