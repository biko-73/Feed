# -*- coding: utf-8 -*-
# TNPosterXDownloadThread.py - Standalone Downloader
# By Enigma2 Developer (2025)

import os
import re
import requests
from urllib.parse import quote

# --- مفاتيح API ---
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

# --- حجم الصورة ---
isz = "185,278"  # للبوستر
bsz = "1920,1080"  # للخلفية

# --- User Agent ---
headers = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
}

def download_poster(dwn_poster, title, shortdesc, fulldesc):
	try:
		if not title or os.path.exists(dwn_poster):
			return False
		query = quote(title)
		url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language=en"
		resp = requests.get(url, headers=headers, timeout=10)
		if resp.status_code == 200:
			data = resp.json()
			if data.get("results"):
				poster_path = data["results"][0].get("poster_path")
				if poster_path:
					img_url = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
					return save_image(img_url, dwn_poster)
		return False
	except Exception as e:
		if os.path.exists(dwn_poster):
			os.remove(dwn_poster)
		return False

def download_backdrop(dwn_backdrop, title, shortdesc, fulldesc):
	try:
		if not title or os.path.exists(dwn_backdrop):
			return False
		query = quote(title)
		url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language=en"
		resp = requests.get(url, headers=headers, timeout=10)
		if resp.status_code == 200:
			data = resp.json()
			if data.get("results"):
				movie_id = data["results"][0].get("id")
				if movie_id:
					details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api}&language=en"
					details_resp = requests.get(details_url, headers=headers, timeout=10)
					if details_resp.status_code == 200:
						details = details_resp.json()
						backdrop_path = details.get("backdrop_path")
						if backdrop_path:
							img_url = f"https://image.tmdb.org/t/p/w{bsz.split(',')[0]}{backdrop_path}"
							return save_image(img_url, dwn_backdrop)
		return False
	except Exception as e:
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