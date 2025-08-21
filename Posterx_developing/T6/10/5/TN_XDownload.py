# -*- coding: utf-8 -*-
import threading
import requests
import os
import time

LOG_FILE = "/media/hdd/logs/TN_X.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

class TN_X_Downloader(threading.Thread):
    def __init__(self, folders, lng="en"):
        threading.Thread.__init__(self)
        self.folders = folders
        self.lng = lng
        self.daemon = True
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enigma2 - TN_X"})

    def run(self):
        tn_log("[DOWNLOADER] الخيط يعمل...")
        while True:
            time.sleep(1)

    def download(self, title, clean_name):
        try:
            tn_log(f"[DOWNLOAD] بدء البحث عن: {title}")
            query = requests.utils.quote(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={self.lng}"
            tn_log(f"[TMDB] طلب (lang={self.lng}): {url}")
            resp = self.session.get(url, timeout=8)
            if resp.status_code != 200:
                return False
            data = resp.json()
            if not data.get("results"):
                return False

            for res in data["results"]:
                media_type = res.get("media_type")
                if media_type not in ["movie", "tv"]:
                    continue
                tmdb_id = res.get("id")
                if not tmdb_id:
                    continue

                details_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={tmdb_api}&language={self.lng}&append_to_response=images"
                details = self.session.get(details_url, timeout=10).json()

                if res.get("poster_path"):
                    self.download_image(f"https://image.tmdb.org/t/p/w342{res['poster_path']}", os.path.join(self.folders["poster"], f"{clean_name}.jpg"))
                if details.get("backdrop_path"):
                    self.download_image(f"https://image.tmdb.org/t/p/w1280{details['backdrop_path']}", os.path.join(self.folders["backdrop"], f"{clean_name}.jpg"))
                if "images" in details:
                    logos = details["images"].get("logos", [])
                    if logos:
                        best_logo = sorted(logos, key=lambda x: x.get("vote_count", 0), reverse=True)[0]
                        self.download_image(f"https://image.tmdb.org/t/p/original{best_logo['file_path']}", os.path.join(self.folders["logo"], f"{clean_name}.png"))
                    backdrops = details["images"].get("backdrops", [])
                    horizontal_backdrops = [b for b in backdrops if b.get("aspect_ratio", 0) > 1.5]
                    if horizontal_backdrops:
                        best_banner = sorted(horizontal_backdrops, key=lambda x: x.get("vote_average", 0), reverse=True)[0]
                        self.download_image(f"https://image.tmdb.org/t/p/w780{best_banner['file_path']}", os.path.join(self.folders["banner"], f"{clean_name}.jpg"))
                return True
            return False
        except Exception as e:
            tn_log(f"[ERROR] تنزيل: {e}")
            return False

    def download_image(self, url, filename):
        try:
            tn_log(f"[IMAGE] تنزيل من: {url}")
            r = self.session.get(url, timeout=8, stream=True)
            if r.status_code == 200:
                tmp_file = filename + ".tmp"
                with open(tmp_file, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                os.rename(tmp_file, filename)
                tn_log(f"[IMAGE] تم الحفظ: {filename}")
                return True
        except Exception as e:
            tn_log(f"[IMAGE] خطأ: {e}")
        return False