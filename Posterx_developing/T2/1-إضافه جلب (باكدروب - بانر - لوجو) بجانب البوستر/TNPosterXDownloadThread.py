# -*- coding: utf-8 -*-
# PosterX - تنزيل البوسترات والخلفيات من مصادر متعددة
# مطور: مُعدّل من digiteng, sunriser, beber + تطوير شامل
# دعم TMDb, Fanart.tv, TheTVDB, Google
# 2025

import os
import sys
import re
import requests
import threading
from configparser import ConfigParser

PY3 = sys.version_info[0] == 3

try:
    if PY3:
        from urllib.parse import quote
    else:
        from urllib2 import quote
except:
    quote = lambda s: s

# --- قراءة المفاتيح من ملف الإعدادات ---
CONFIG_FILE = "/etc/enigma2/PosterX.conf"

def load_api_keys():
    config = {
        'tmdb_api': '3c3efcf47c3577558812bb9d64019d65',
        'fanart_api': '6d231536dea4318a88cb2520ce89473b',
        'thetvdb_api': 'a99d487bb3426e5f3a60dea6d3d3c7ef',
        'omdb_api': 'cb1d9f55',
        'language': 'ar',
        'fallback_sources': True
    }

    if os.path.exists(CONFIG_FILE):
        try:
            cfg = ConfigParser()
            if PY3:
                cfg.read(CONFIG_FILE, encoding='utf-8')
            else:
                cfg.read(CONFIG_FILE)

            if cfg.has_section('API_KEYS'):
                for key in ['tmdb_api', 'fanart_api', 'thetvdb_api', 'omdb_api']:
                    if cfg.has_option('API_KEYS', key):
                        config[key] = cfg.get('API_KEYS', key)

            if cfg.has_section('SETTINGS'):
                if cfg.has_option('SETTINGS', 'language'):
                    config['language'] = cfg.get('SETTINGS', 'language')
                if cfg.has_option('SETTINGS', 'fallback_sources'):
                    config['fallback_sources'] = cfg.getboolean('SETTINGS', 'fallback_sources')

        except Exception as e:
            print(f"[PosterX] Error reading config: {e}")

    return config

API_KEYS = load_api_keys()

# حجم الصورة الافتراضي
isz = "185,278"  # العرض, الارتفاع للبوستر

# --- مجلدات الحفظ ---
path_folder = "/media/hdd/Poster_X/"
if not os.path.isdir(path_folder):
    path_folder = "/media/usb/Poster_X/"
if not os.path.isdir(path_folder):
    path_folder = "/tmp/Poster_X/"

os.makedirs(path_folder, exist_ok=True)
os.makedirs(os.path.join(path_folder, "backdrops"), exist_ok=True)
os.makedirs(os.path.join(path_folder, "banners"), exist_ok=True)
os.makedirs(os.path.join(path_folder, "logos"), exist_ok=True)

backdrop_folder = os.path.join(path_folder, "backdrops/")
banner_folder = os.path.join(path_folder, "banners/")
logo_folder = os.path.join(path_folder, "logos/")


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

            # استخراج السنة
            year_match = re.search(r'\b(19|20)\d{2}\b', fd)
            year = year_match.group(0) if year_match else None

            # تحديد النوع
            if any(word in fd.lower() for word in ["film", "movie", "фильм", "кино", "cinema"]):
                srch = "movie"
            elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
                srch = "tv"

            # --- المرحلة 1: جلب من TMDb ---
            success, log = self._fetch_from_tmdb(dwn_poster, title, year, srch, fd)
            if success:
                return True, log

            # --- المرحلة 2: المصادر البديلة ---
            if API_KEYS.get('fallback_sources', True):
                if 'tv' in srch or 'series' in fd.lower():
                    success, log = self._fetch_from_thetvdb(dwn_poster, title, year)
                    if success:
                        return True, log
                # Google كمصدر أخير
                success, log = self._fetch_from_google(dwn_poster, title, shortdesc, fulldesc)
                if success:
                    return True, log

            return False, "[All Sources Failed]"

        except Exception as e:
            return False, f"[ERROR] {str(e)}"

    def _fetch_from_tmdb(self, dwn_poster, title, year, srch, fd):
        try:
            query = quote(title)
            url = f"https://api.themoviedb.org/3/search/{srch}?api_key={API_KEYS['tmdb_api']}&query={query}"
            if year:
                url += f"&year={year}"
            url += f"&language={API_KEYS['language']}"

            resp = requests.get(url, timeout=10).json()
            if not resp.get("results"):
                return False, "[TMDb] No results"

            result = resp["results"][0]
            media_id = result["id"]
            media_type = result.get("media_type", srch)
            poster_path = result.get("poster_path")

            base_folder = os.path.dirname(dwn_poster)
            basename = os.path.splitext(os.path.basename(dwn_poster))[0]

            # --- تنزيل البوستر ---
            if poster_path:
                url_poster = f"https://image.tmdb.org/t/p/w{isz.split(',')[0]}{poster_path}"
                self.savePoster(dwn_poster, url_poster)

            # --- جلب التفاصيل الكاملة ---
            details_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}?api_key={API_KEYS['tmdb_api']}&append_to_response=images,external_ids"
            details = requests.get(details_url, timeout=10).json()

            # --- 1. Backdrop ---
            if details.get("backdrop_path"):
                backdrop_file = os.path.join(backdrop_folder, f"{basename}_backdrop.jpg")
                url_backdrop = f"https://image.tmdb.org/t/p/w1280{details['backdrop_path']}"
                self.savePoster(backdrop_file, url_backdrop)

            # --- 2. Fanart.tv ---
            tvdb_id = details.get("external_ids", {}).get("tvdb_id") if media_type == "tv" else None
            self._fetch_from_fanarttv(media_id, tvdb_id, media_type, base_folder, basename)

            return True, f"[TMDb OK] {title}"

        except Exception as e:
            print(f"[TMDb] Error: {e}")
            return False, f"[TMDb] Failed: {e}"

    def _fetch_from_fanarttv(self, tmdb_id, tvdb_id, media_type, base_folder, basename):
        try:
            if not API_KEYS.get('fanart_api'):
                return

            if media_type == "movie" and tmdb_id:
                url = f"https://webservice.fanart.tv/v3/movies/{tmdb_id}?api_key={API_KEYS['fanart_api']}"
            elif tvdb_id:
                url = f"https://webservice.fanart.tv/v3/tv/{tvdb_id}?api_key={API_KEYS['fanart_api']}"
            else:
                return

            data = requests.get(url, timeout=10).json()

            # Logo (PNG)
            if data.get("hdmovielogo"):
                logo_file = os.path.join(logo_folder, f"{basename}_logo.png")
                self.savePoster(logo_file, data["hdmovielogo"][0]["url"])
            elif data.get("hdtvlogo"):
                logo_file = os.path.join(logo_folder, f"{basename}_logo.png")
                self.savePoster(logo_file, data["hdtvlogo"][0]["url"])

            # Banner
            if data.get("moviebanner"):
                banner_file = os.path.join(banner_folder, f"{basename}_banner.jpg")
                self.savePoster(banner_file, data["moviebanner"][0]["url"])
            elif data.get("tvbanner"):
                banner_file = os.path.join(banner_folder, f"{basename}_banner.jpg")
                self.savePoster(banner_file, data["tvbanner"][0]["url"])

            # Fanart (خلفية أفضل)
            if data.get("moviethumb") or data.get("moviebackground"):
                fanart = (data.get("moviethumb") or data.get("moviebackground"))[0]["url"]
                fanart_file = os.path.join(backdrop_folder, f"{basename}_fanart.jpg")
                self.savePoster(fanart_file, fanart)

        except Exception as e:
            print(f"[Fanart.tv] Error: {e}")

    def _fetch_from_thetvdb(self, dwn_poster, title, year):
        try:
            if not API_KEYS.get('thetvdb_api'):
                return False, "[TheTVDB] No API Key"

            headers = {"Authorization": f"Bearer {API_KEYS['thetvdb_api']}", "Content-Type": "application/json"}
            url = f"https://api4.thetvdb.com/v4/search?query={quote(title)}&type=series"
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code != 200:
                return False, "[TheTVDB] Auth Failed"

            data = resp.json()
            if not data.get("data"):
                return False, "[TheTVDB] No results"

            series_id = data["data"][0]["id"]
            details_url = f"https://api4.thetvdb.com/v4/series/{series_id}"
            details = requests.get(details_url, headers=headers, timeout=10).json()

            if not details.get("data"):
                return False, "[TheTVDB] No details"

            # محاولة جلب صورة
            if details["data"].get("image"):
                image_url = f"https://thetvdb.com{details['data']['image']}"
                self.savePoster(dwn_poster, image_url)
                return True, f"[TheTVDB OK] {title}"

            return False, "[TheTVDB] No image"

        except Exception as e:
            return False, f"[TheTVDB] Error: {e}"

    def _fetch_from_google(self, dwn_poster, title, shortdesc, fulldesc, channel=None):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            query = quote(title)
            url = f"https://www.google.com/search?q={query}+movie+tv+poster&tbm=isch&tbs=ift:jpg,isz:m"
            resp = requests.get(url, headers=headers, timeout=10).text
            match = re.search(r'\],\["https://([^"]+\.jpe?g)",\d+,\d+]', resp)
            if match:
                img_url = "https://" + match.group(1).split("&")[0]
                self.savePoster(dwn_poster, img_url)
                return True, f"[Google OK] {title}"
            return False, "[Google] Not found"
        except:
            return False, "[Google Error]"

    def savePoster(self, dwn_poster, url_poster):
        try:
            r = requests.get(url_poster, stream=True, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                ext = ".png" if url_poster.lower().endswith('.png') else ".jpg"
                if not dwn_poster.lower().endswith(ext):
                    dwn_poster = dwn_poster.rsplit('.', 1)[0] + ext
                with open(dwn_poster, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
        except Exception as e:
            print(f"[PosterX] Save error: {e}")