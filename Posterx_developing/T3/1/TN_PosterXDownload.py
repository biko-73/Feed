# -*- coding: utf-8 -*-
# TN_PosterXDownload.py - خيط تنزيل البوسترات
# دعم: TMDB, TVDB, Fanart.tv, OMDb

import os
import re
import requests
import threading
from queue import Empty

# --- API Keys ---
tmdb_api = "3c3efcf47c3577558812bb9d64019d65"
tvdb_key = "a99d487bb3426e5f3a60dea6d3d3c7ef"
omdb_api = "cb1d9f55"
fanart_api = "6d231536dea4318a88cb2520ce89473b"

class TNPosterXDownloader(threading.Thread):
    def __init__(self, poster_folder, lang="en"):
        threading.Thread.__init__(self)
        self.poster_folder = poster_folder
        self.lang = lang
        self.daemon = True
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enigma2 - TN_PosterX"})

    def run(self):
        while True:
            try:
                item = self.download_queue.get(timeout=30)
                self.download_poster(item)
                self.download_queue.task_done()
            except Empty:
                break
            except:
                continue

    def download_poster(self, item):
        filename = item["filename"]
        title = item["title"]
        short = item["short"]
        full = item["full"]
        lang = item["lang"]

        # لا تعيد التنزيل إذا كان الملف حديثًا (أقل من 24 ساعة)
        if os.path.exists(filename):
            if time.time() - os.path.getmtime(filename) < 86400:
                return

        # أولوية: TMDB > TVDB > Fanart > OMDb
        if self.search_tmdb(title, short + " " + full, lang, filename):
            return
        if "series" in (short + full).lower() or "episode" in (short + full).lower():
            if self.search_tvdb(title, short + " " + full, lang, filename):
                return
        if self.search_fanart(title, short + " " + full, lang, filename):
            return
        if self.search_omdb(title, short + " " + full, lang, filename):
            return

    def search_tmdb(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
            resp = self.session.get(url, timeout=10).json()
            if resp.get("results"):
                for res in resp["results"]:
                    if res.get("poster_path"):
                        img_url = f"https://image.tmdb.org/t/p/w342{res['poster_path']}"
                        return self.download_image(img_url, filename)
        except:
            pass
        return False

    def search_tvdb(self, title, desc, lang, filename):
        # TVDB يتطلب Authentication Token (يحتاج تحسين لاحقًا)
        return False

    def search_fanart(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"https://webservice.fanart.tv/v3/search?api_key={fanart_api}&name={query}"
            resp = self.session.get(url, timeout=10).json()
            if resp.get("tv") and resp["tv"]:
                art = resp["tv"][0].get("tvposter")
                if art:
                    return self.download_image(art[0]["url"], filename)
            if resp.get("movie") and resp["movie"]:
                art = resp["movie"][0].get("movieposter")
                if art:
                    return self.download_image(art[0]["url"], filename)
        except:
            pass
        return False

    def search_omdb(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"http://www.omdbapi.com/?t={query}&apikey={omdb_api}&r=json"
            resp = self.session.get(url, timeout=10).json()
            if resp.get("Poster") and "noposter" not in resp["Poster"]:
                return self.download_image(resp["Poster"], filename)
        except:
            pass
        return False

    def download_image(self, url, filename):
        try:
            r = self.session.get(url, timeout=10, stream=True)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                return True
        except:
            pass
        return False