# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import re
import requests
import threading
import time
from queue import Empty

from .TN_XTools import clean_title
from .TN_title_mapping import TITLE_MAPPING

LOG_FILE = "/media/hdd/logs/TN_X.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tmdb_api = "3c3efcf47c3577558812bb9d64019d65"

class TN_X_Downloader(threading.Thread):
    def __init__(self, download_queue, folders, lng="en", pending_requests=None, on_download_complete=None):
        threading.Thread.__init__(self)
        self.download_queue = download_queue
        self.folders = folders
        self.lng = lng
        self.pending_requests = pending_requests or set()
        self.on_download_complete = on_download_complete
        self.daemon = True
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Enigma2 - TN_X"})

    def run(self):
        tn_log("[DOWNLOADER] الخيط يعمل...")
        while True:
            try:
                item = self.download_queue.get(timeout=30)
                tn_log(f"[QUEUE] معالجة: {item['title']}")
                self.download_all(item)
                self.download_queue.task_done()
            except Empty:
                tn_log("[DOWNLOADER] لا مهام - الاستمرار...")
                continue
            except Exception as e:
                tn_log(f"[DOWNLOADER] خطأ: {e}")
                continue

    def download_all(self, item):
        title = item["title"]
        desc = item["short"] + " " + item["full"]
        clean_name = item["clean_name"]
        langs = item.get("langs", ["en"])

        # تطبيق التحويل
        mapped_title = TITLE_MAPPING.get(title.strip(), title)
        tn_log(f"[MAPPING] '{title}' → '{mapped_title}'")
        title = mapped_title

        poster_file = os.path.join(self.folders["poster"], f"{clean_name}.jpg")
        backdrop_file = os.path.join(self.folders["backdrop"], f"{clean_name}.jpg")
        logo_file = os.path.join(self.folders["logo"], f"{clean_name}.png")
        banner_file = os.path.join(self.folders["banner"], f"{clean_name}.jpg")
        rating_file = os.path.join(self.folders["rating"], f"{clean_name}.txt")
        score_file = os.path.join(self.folders["rating"], f"{clean_name}_score.txt")

        recent = [f for f in [poster_file, backdrop_file] if os.path.exists(f) and time.time() - os.path.getmtime(f) < 86400]
        if recent:
            self.remove_from_pending(poster_file)
            return

        for lang in langs:
            result = self.search_tmdb(title, desc, lang, clean_name, poster_file, backdrop_file, logo_file, banner_file, rating_file, score_file)
            if result:
                tn_log(f"[SUCCESS] تم التنزيل (lang={lang})")
                self.remove_from_pending(poster_file)
                if self.on_download_complete:
                    self.on_download_complete(clean_name)
                return

        tn_log(f"[FAIL] فشل جميع اللغات لـ: {title}")
        self.remove_from_pending(poster_file)

    def remove_from_pending(self, filename):
        if filename in self.pending_requests:
            self.pending_requests.remove(filename)

    def search_tmdb(self, title, desc, lang, clean_name, poster_file, backdrop_file, logo_file, banner_file, rating_file, score_file):
        try:
            query = requests.utils.quote(title)
            url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api}&query={query}&language={lang}"
            tn_log(f"[TMDB] طلب (lang={lang}): {url}")
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

                details = self.get_details(media_type, tmdb_id, lang)
                if not details:
                    continue

                if res.get("poster_path"):
                    self.download_image(f"https://image.tmdb.org/t/p/w342{res['poster_path']}", poster_file)
                if details.get("backdrop_path"):
                    self.download_image(f"https://image.tmdb.org/t/p/w1280{details['backdrop_path']}", backdrop_file)

                if "images" in details:
                    logos = details["images"].get("logos", [])
                    arabic_logos = [l for l in logos if l.get("iso_639_1") == "ar"]
                    logo_list = arabic_logos or logos
                    if logo_list:
                        best_logo = sorted(logo_list, key=lambda x: x.get("vote_count", 0), reverse=True)[0]
                        self.download_image(f"https://image.tmdb.org/t/p/original{best_logo['file_path']}", logo_file)

                    backdrops = details["images"].get("backdrops", [])
                    horizontal_backdrops = [b for b in backdrops if b.get("aspect_ratio", 0) > 1.5]
                    if horizontal_backdrops:
                        best_banner = sorted(horizontal_backdrops, key=lambda x: x.get("vote_average", 0), reverse=True)[0]
                        self.download_image(f"https://image.tmdb.org/t/p/w780{best_banner['file_path']}", banner_file)

                rating = self.extract_rating(details, media_type)
                with open(rating_file, "w", encoding="utf-8") as f:
                    f.write(rating)
                tn_log(f"[RATING] تم حفظ التقييم: {rating}")

                vote_avg = details.get("vote_average", 0)
                with open(score_file, "w") as f:
                    f.write(str(vote_avg))
                tn_log(f"[SCORE] تم حفظ النجوم: {vote_avg}")

                return True
            return False
        except Exception as e:
            tn_log(f"[SEARCH] خطأ: {e}")
            return False

    def get_details(self, media_type, tmdb_id, lang):
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={tmdb_api}&language={lang}&append_to_response=images,credits,content_ratings,release_dates"
            tn_log(f"[DETAILS] جلب تفاصيل: {url}")
            resp = self.session.get(url, timeout=10)
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception as e:
            tn_log(f"[DETAILS] خطأ: {e}")
            return None

    def extract_rating(self, details, media_type):
        try:
            if media_type == "tv":
                for r in details.get("content_ratings", {}).get("results", []):
                    if r.get("iso_3166_1") in ["US", "GB", "AE", self.lng.upper()]:
                        rating = r.get("rating", "PG")
                        tn_log(f"[RATING] تم جلب تصنيف TV: {rating}")
                        return rating
            elif media_type == "movie":
                for r in details.get("release_dates", {}).get("results", []):
                    if r.get("iso_3166_1") in ["US", "GB", "AE", self.lng.upper()]:
                        certification = r.get("release_dates", [{}])[0].get("certification", "PG")
                        tn_log(f"[RATING] تم جلب تصنيف فيلم: {certification}")
                        return certification
            return "PG"
        except Exception as e:
            tn_log(f"[RATING] خطأ: {e}")
            return "PG"

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
            tn_log(f"[IMAGE] خطأ في التنزيل: {e}")
        return False