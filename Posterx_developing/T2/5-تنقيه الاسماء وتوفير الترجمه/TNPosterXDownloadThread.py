# -*- coding: utf-8 -*-
from threading import Thread
from .TN_lib import search_movie_smart, get_tmdb_data, get_fanarttv, find_by_imdb_id
from .TN_Utils import convtext, log, setup_folders
import os
import sys

try:
    if sys.version_info[0] == 3:
        import queue
    else:
        import Queue as queue
except:
    pass

# --- تهيئة المجلدات وتسجيل الدخول ---
FOLDERS, _ = setup_folders("TN_X")

class TNPosterXDownloadThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = queue.LifoQueue()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            canal = self.queue.get()
            self.download(canal)
            self.queue.task_done()

    def download(self, canal):
        title = canal[2]
        fulldesc = canal[3]
        shortdesc = canal[4]
        event_name = canal[5]
        dwn_poster = os.path.join(FOLDERS["poster"], f"{event_name}.jpg")

        if os.path.exists(dwn_poster) and os.path.getsize(dwn_poster) > 0:
            return

        # --- استخراج السنة ---
        year_match = re.search(r'\b(19|20)\d{2}\b', f"{title} {shortdesc} {fulldesc}")
        year = year_match.group(0) if year_match else None

        # --- البحث الذكي ---
        result = search_movie_smart(title, year, shortdesc, fulldesc)
        if not result:
            log(f"[Download] Not found: {title}")
            return

        # --- تحديد النوع ---
        media_type = "movie" if result.get("title") else "tv"
        tmdb_id = result["id"]

        # --- جلب البيانات الكاملة ---
        data = get_tmdb_data(tmdb_id, media_type)
        if not 
            return

        basename = convtext(data.get("title") or data.get("name") or "Unknown")

        # --- 1. تنزيل البوستر ---
        if data.get("poster_path"):
            url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            path = os.path.join(FOLDERS["poster"], f"{basename}.jpg")
            self.save_image(path, url)

        # --- 2. تنزيل الباكدروب ---
        if data.get("backdrop_path"):
            url = f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}"
            path = os.path.join(FOLDERS["backdrop"], f"{basename}_backdrop.jpg")
            self.save_image(path, url)

        # --- 3. جلب من Fanart.tv ---
        tvdb_id = data.get("external_ids", {}).get("tvdb_id")
        fanart = get_fanarttv(tmdb_id, tvdb_id, "tv" if tvdb_id else "movie")
        if fanart:
            self.save_fanart(fanart, basename)

    def save_fanart(self, data, basename):
        # --- Logo ---
        if data.get("hdmovielogo"):
            path = os.path.join(FOLDERS["logo"], f"{basename}_logo.png")
            self.save_image(path, data["hdmovielogo"][0]["url"])
        elif data.get("hdtvlogo"):
            path = os.path.join(FOLDERS["logo"], f"{basename}_logo.png")
            self.save_image(path, data["hdtvlogo"][0]["url"])

        # --- Banner ---
        if data.get("moviebanner"):
            path = os.path.join(FOLDERS["banner"], f"{basename}_banner.jpg")
            self.save_image(path, data["moviebanner"][0]["url"])
        elif data.get("tvbanner"):
            path = os.path.join(FOLDERS["banner"], f"{basename}_banner.jpg")
            self.save_image(path, data["tvbanner"][0]["url"])

    def save_image(self, path, url):
        try:
            resp = SESSION.get(url, timeout=10, stream=True)
            if resp.status_code == 200:
                ext = ".png" if url.lower().endswith('.png') else ".jpg"
                if not path.lower().endswith(ext):
                    path = path.rsplit('.', 1)[0] + ext
                with open(path, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                log(f"[Download] Saved: {path}")
        except Exception as e:
            log(f"[Error] Failed to save {url}: {e}")