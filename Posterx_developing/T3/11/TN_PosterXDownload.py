# -*- coding: utf-8 -*-
import os
import re
import requests
import threading
from queue import Empty

LOG_FILE = "/media/hdd/logs/TN_PosterX.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

class TNPosterXDownloader(threading.Thread):
    def __init__(self, download_queue, poster_folder, lng="en", pending_requests=None, on_download_complete=None):
        threading.Thread.__init__(self)
        self.download_queue = download_queue
        self.poster_folder = poster_folder
        self.lng = lng
        self.pending_requests = pending_requests or set()
        self.on_download_complete = on_download_complete
        self.daemon = True
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enigma2 - TN_PosterX"})

    def run(self):
        tn_log("[DOWNLOADER] الخيط يعمل...")
        while True:
            try:
                item = self.download_queue.get(timeout=30)
                tn_log(f"[QUEUE] معالجة: {item['title']}")
                self.download_poster(item)
                self.download_queue.task_done()
            except Empty:
                tn_log("[DOWNLOADER] لا مهام - الاستمرار...")
                continue
            except Exception as e:
                tn_log(f"[DOWNLOADER] خطأ: {e}")
                continue

    def download_poster(self, item):
        filename = item["filename"]
        title = item["title"]
        short = item["short"]
        full = item["full"]
        langs = item.get("langs", ["en"])
        tn_log(f"[DOWNLOAD] بدء البحث عن: {title}")

        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            age = time.time() - os.path.getmtime(filename)
            if age < 86400:
                tn_log(f"[CACHE] ملف حديث - تخطي")
                if filename in self.pending_requests:
                    self.pending_requests.remove(filename)
                return

        # --- البحث بلغات متعددة ---
        for lang in langs:
            if self.search_tmdb(title, short + " " + full, lang, filename):
                tn_log(f"[SUCCESS] تم التنزيل من TMDB (lang={lang})")
                if filename in self.pending_requests:
                    self.pending_requests.remove(filename)
                if self.on_download_complete:
                    self.on_download_complete(filename)
                return

        tn_log(f"[FAIL] فشل جميع اللغات لـ: {title}")
        if filename in self.pending_requests:
            self.pending_requests.remove(filename)

    def search_tmdb(self, title, desc, lang, filename):
        try:
            # تجربة اسم أبسط
            query = requests.utils.quote(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
            tn_log(f"[TMDB] طلب (lang={lang}): {url}")
            resp = self.session.get(url, timeout=8)
            if resp.status_code != 200:
                tn_log(f"[TMDB] خطأ HTTP: {resp.status_code}")
                return False
            data = resp.json()
            if data.get("results"):
                for res in data["results"]:
                    if res.get("poster_path"):
                        img_url = f"https://image.tmdb.org/t/p/w342{res['poster_path']}"
                        tn_log(f"[TMDB] وجدت بوستر: {img_url} (lang={lang})")
                        return self.download_image(img_url, filename)
            return False
        except Exception as e:
            tn_log(f"[TMDB] خطأ: {e}")
            return False

    def download_image(self, url, filename):
        try:
            tn_log(f"[IMAGE] تنزيل من: {url}")
            r = self.session.get(url, timeout=8, stream=True)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                tn_log(f"[IMAGE] تم الحفظ: {filename}")
                return True
        except Exception as e:
            tn_log(f"[IMAGE] خطأ في التنزيل: {e}")
        return False