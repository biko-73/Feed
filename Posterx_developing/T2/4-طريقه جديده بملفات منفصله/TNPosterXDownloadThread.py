# -*- coding: utf-8 -*-
from threading import Thread
from .TN_lib import search_tmdb, get_tmdb_data, get_fanarttv, find_by_imdb_id
from .TN_Utils import convtext
import os

# --- سيتم تعريف FOLDERS و log لاحقًا ---
FOLDERS = None
log = lambda x: None

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

        if os.path.exists(dwn_poster):
            return

        # --- 1. جلب عبر IMDb ID ---
        imdb_match = re.search(r'tt\d{7,8}', fulldesc)
        if imdb_match:
            result = find_by_imdb_id(imdb_match.group(0))
            if result:
                data = get_tmdb_data(result["id"], "movie")
                self.save_media(data, event_name)
                return

        # --- 2. جلب عبر TMDb ---
        result = search_tmdb(title)
        if result:
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(result["id"], media_type)
            self.save_media(data, event_name)

    def save_media(self, data, basename):
        if not data:
            return

        # --- Poster ---
        if data.get("poster_path"):
            url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
            path = os.path.join(FOLDERS["poster"], f"{basename}.jpg")
            self.save_image(path, url)

        # --- Backdrop ---
        if data.get("backdrop_path"):
            url = f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}"
            path = os.path.join(FOLDERS["backdrop"], f"{basename}_backdrop.jpg")
            self.save_image(path, url)

        # --- Fanart.tv ---
        tvdb_id = data.get("external_ids", {}).get("tvdb_id")
        fanart = get_fanarttv(data.get("id"), tvdb_id, "tv" if tvdb_id else "movie")
        if fanart:
            self.save_fanart(fanart, basename)

    def save_fanart(self, data, basename):
        if data.get("hdmovielogo"):
            path = os.path.join(FOLDERS["logo"], f"{basename}_logo.png")
            self.save_image(path, data["hdmovielogo"][0]["url"])
        if data.get("moviebanner"):
            path = os.path.join(FOLDERS["banner"], f"{basename}_banner.jpg")
            self.save_image(path, data["moviebanner"][0]["url"])

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