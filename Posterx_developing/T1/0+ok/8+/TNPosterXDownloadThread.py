# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py - Light Functions
# By Enigma2 Developer (2025)

import os
import re
import requests
from urllib.parse import quote

# --- مفاتيح API ---
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

# --- حجم الصورة ---
isz = "185,278"
bsz = "1920,1080"

# --- User Agent ---
headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def download_poster(dwn_poster, title, shortdesc, fulldesc):
	try:
		if not title:
			return False
		query = quote(title)
		url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language=en"
		resp = requests.get(url, headers=headers, timeout=10).json()
		if resp.get("results"):
			poster_path = resp["results"][0].get("poster_path")
			if poster_path:
				url_poster = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
				return save_image(url_poster, dwn_poster)
		return False
	except:
		if os.path.exists(dwn_poster):
			os.remove(dwn_poster)
		return False

def download_backdrop(dwn_backdrop, title, shortdesc, fulldesc):
	try:
		if not title:
			return False
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
					return save_image(url_backdrop, dwn_backdrop)
		return False
	except:
		if os.path.exists(dwn_backdrop):
			os.remove(dwn_backdrop)
		return False

def save_image(url, filepath):
	try:
		r = requests.get(url, headers=headers, stream=True, timeout=10, allow_redirects=True)
		if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
			with open(filepath, 'wb') as f:
				for chunk in r.iter_content(1024):
					f.write(chunk)
			return os.path.exists(filepath) and os.path.getsize(filepath) > 0
	except:
		pass
	return False