# -*- coding: utf-8 -*-
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

LOG_FILE = "/media/hdd/logs/TN_PosterX.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

class TNPosterXDownloader(threading.Thread):
    def __init__(self, poster_folder, lang="en"):
        threading.Thread.__init__(self)
        self.poster_folder = poster_folder
        self.lang = lang
        self.daemon = True
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enigma2 - TN_PosterX"})
        tn_log("[DOWNLOADER] تم تهيئة خيط التنزيل")

    def run(self):
        tn_log("[DOWNLOADER] بدء تشغيل الخيط")
        while True:
            try:
                item = download_queue.get(timeout=60)
                tn_log(f"[QUEUE] معالجة: {item['title']}")
                self.download_poster(item)
                download_queue.task_done()
            except Empty:
                tn_log("[DOWNLOADER] لا مهام - إيقاف")
                break
            except Exception as e:
                tn_log(f"[DOWNLOADER] خطأ: {e}")
                break

    def download_poster(self, item):
        filename = item["filename"]
        title = item["title"]
        short = item["short"]
        full = item["full"]
        lang = item["lang"]
        tn_log(f"[DOWNLOAD] بدء البحث عن: {title}")

        # تجاهل إذا حديث
        if os.path.exists(filename):
            age = time.time() - os.path.getmtime(filename)
            if age < 86400:
                tn_log(f"[CACHE] الملف جديد ({age:.0f}s) - تخطي")
                return

        # أولوية البحث
        sources = [
            ("TMDB", self.search_tmdb),
            ("TVDB", self.search_tvdb),
            ("Fanart", self.search_fanart),
            ("OMDb", self.search_omdb)
        ]

        for src_name, src_func in sources:
            tn_log(f"[SOURCE] محاولة من {src_name}...")
            if src_func(title, short + " " + full, lang, filename):
                tn_log(f"[SUCCESS] تم التنزيل من {src_name}: {filename}")
                return

        tn_log(f"[FAIL] فشل جميع المصادر لـ: {title}")

    def search_tmdb(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
            tn_log(f"[TMDB] طلب: {url}")
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                tn_log(f"[TMDB] خطأ HTTP: {resp.status_code}")
                return False
            data = resp.json()
            if data.get("results"):
                for res in data["results"]:
                    if res.get("poster_path"):
                        img_url = f"https://image.tmdb.org/t/p/w342{res['poster_path']}"
                        tn_log(f"[TMDB] وجدت بوستر: {img_url}")
                        return self.download_image(img_url, filename)
                tn_log("[TMDB] لا يوجد poster_path")
            else:
                tn_log("[TMDB] لا نتائج")
            return False
        except Exception as e:
            tn_log(f"[TMDB] استثناء: {e}")
            return False

    def search_tvdb(self, title, desc, lang, filename):
        tn_log("[TVDB] غير مدعوم مؤقتًا (يتطلب token)")
        return False

    def search_fanart(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"https://webservice.fanart.tv/v3/search?api_key={fanart_api}&name={query}"
            tn_log(f"[FANART] طلب: {url}")
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                tn_log(f"[FANART] خطأ HTTP: {resp.status_code}")
                return False
            data = resp.json()
            if data.get("tv"):
                for tv in data["tv"]:
                    if tv.get("tvposter"):
                        img_url = tv["tvposter"][0]["url"]
                        tn_log(f"[FANART] وجدت بوستر مسلسل: {img_url}")
                        return self.download_image(img_url, filename)
            if data.get("movie"):
                for movie in data["movie"]:
                    if movie.get("movieposter"):
                        img_url = movie["movieposter"][0]["url"]
                        tn_log(f"[FANART] وجدت بوستر فيلم: {img_url}")
                        return self.download_image(img_url, filename)
            return False
        except Exception as e:
            tn_log(f"[FANART] استثناء: {e}")
            return False

    def search_omdb(self, title, desc, lang, filename):
        try:
            query = requests.utils.quote(title)
            url = f"http://www.omdbapi.com/?t={query}&apikey={omdb_api}&r=json"
            tn_log(f"[OMDB] طلب: {url}")
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                tn_log(f"[OMDB] خطأ HTTP: {resp.status_code}")
                return False
            data = resp.json()
            if data.get("Poster") and "noposter" not in data["Poster"]:
                tn_log(f"[OMDB] وجدت بوستر: {data['Poster']}")
                return self.download_image(data["Poster"], filename)
            else:
                tn_log("[OMDB] لا يوجد بوستر")
            return False
        except Exception as e:
            tn_log(f"[OMDB] استثناء: {e}")
            return False

    def download_image(self, url, filename):
        try:
            tn_log(f"[IMAGE] تنزيل من: {url}")
            r = self.session.get(url, timeout=10, stream=True)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                tn_log(f"[IMAGE] تم الحفظ: {filename}")
                return True
            else:
                tn_log(f"[IMAGE] خطأ HTTP: {r.status_code}")
        except Exception as e:
            tn_log(f"[IMAGE] خطأ في التنزيل: {e}")
        return False