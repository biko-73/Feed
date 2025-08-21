# -*- coding: utf-8 -*-
# PosterX - Download Poster, Backdrop, Banner, Logo from multiple sources
# Developer: Modified by digiteng, sunriser, beber
# Thanks Lululla for improvment AGPTEAM which support this developed file
# Support for TMDb, Fanart.tv, TheTVDB, Google, manual ID, image quality, smart cleaning
# 2025

import os
import sys
import re
import requests
import threading
import time
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
        'fallback_sources': True,
        'quality': 'HD',
        'max_storage_mb': 1024
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
                for key in ['language', 'fallback_sources', 'quality']:
                    if cfg.has_option('SETTINGS', key):
                        config[key] = cfg.get('SETTINGS', key)
                if cfg.has_option('SETTINGS', 'max_storage_mb'):
                    try:
                        config['max_storage_mb'] = int(cfg.get('SETTINGS', 'max_storage_mb'))
                    except:
                        config['max_storage_mb'] = 1024

            if isinstance(config['fallback_sources'], str):
                config['fallback_sources'] = config['fallback_sources'].lower() == 'true'

        except Exception as e:
            print(f"[PosterX] Error reading config: {e}")

    return config

API_KEYS = load_api_keys()

# --- جودة الصور ---
QUALITY_SIZES = {
    "SD": "w185",
    "HD": "w500",
    "FHD": "w1280",
    "4K": "original"
}
poster_size = QUALITY_SIZES.get(API_KEYS['quality'].upper(), "w500")
backdrop_size = QUALITY_SIZES.get(API_KEYS['quality'].upper(), "w1280")

# --- قراءة الأرقام اليدوية (TMDb/IMDb IDs) ---
def load_manual_ids():
    ids = {}
    try:
        cfg = ConfigParser()
        if PY3:
            cfg.read(CONFIG_FILE, encoding='utf-8')
        else:
            cfg.read(CONFIG_FILE)
        if cfg.has_section('MANUAL_IDS'):
            for k, v in cfg.items('MANUAL_IDS'):
                clean_v = v.strip()
                if clean_v:
                    ids[clean_v] = k
    except Exception as e:
        print(f"[PosterX] Error loading manual IDs: {e}")
    return ids

MANUAL_IDS = load_manual_ids()

# --- استخراج العنوان والسنة من اسم الملف ---
def extract_title_year_from_filename(title):
    if not title:
        return None, None
    # استخراج السنة
    year_match = re.search(r'\b(19|20)\d{2}\b', title)
    year = year_match.group(0) if year_match else None
    # تنظيف الاسم
    clean_title = re.sub(r'\b(1080p|720p|480p|BluRay|WEB-DL|REMASTERED|Extended|AC3|DTS|HDCP|HEVC)\b', '', title, flags=re.I)
    clean_title = re.sub(r'[\.\_\-\(\)\[\]]+', ' ', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    if year:
        clean_title = re.sub(r'\b' + year + r'\b', '', clean_title)
    return clean_title.strip(), year

# --- التحقق من المساحة المتاحة ---
def get_free_space(path):
    try:
        stat = os.statvfs(path)
        return (stat.f_frsize * stat.f_bavail) / (1024 * 1024)  # MB
    except:
        return 0

# --- اختيار أفضل وسيلة تخزين ---
def get_external_storage():
    candidates = []
    for path in ['/media/hdd', '/media/usb', '/tmp']:
        if os.path.exists(path) and os.access(path, os.W_OK):
            free_mb = get_free_space(path)
            if free_mb > 500:  # على الأقل 500MB متاحة
                candidates.append((path, free_mb))
    if candidates:
        best = max(candidates, key=lambda x: x[1])  # الأفضل: الأكثر مساحة
        print(f"[PosterX] Selected storage: {best[0]} (Free: {best[1]:.1f} MB)")
        return best[0]
    # إذا لم يتوفر، استخدم /tmp كحل أخير
    if os.access('/tmp', os.W_OK) and get_free_space('/tmp') > 100:
        print("[PosterX] Using /tmp as fallback storage")
        return '/tmp'
    print("[PosterX] No suitable storage found!")
    return '/tmp'

# --- إنشاء الهيكل ---
base_storage = get_external_storage()
main_folder = os.path.join(base_storage, "TNPoster_X")
FOLDERS = {
    "poster": os.path.join(main_folder, "Poster_X"),
    "backdrop": os.path.join(main_folder, "backdrops_X"),
    "banner": os.path.join(main_folder, "banners_X"),
    "logo": os.path.join(main_folder, "logos_X")
}
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

# --- تنظيف ذكي حسب المساحة ---
def smart_cleanup(folder, max_mb=1024):
    try:
        max_bytes = max_mb * 1024 * 1024
        files = [
            (os.path.join(folder, f), os.path.getmtime(os.path.join(folder, f)), os.path.getsize(os.path.join(folder, f)))
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        files.sort(key=lambda x: x[1])  # الأقدم أولًا
        total_size = sum(size for _, _, size in files)
        while total_size > max_bytes and files:
            f_path, _, size = files.pop(0)
            os.remove(f_path)
            total_size -= size
    except Exception as e:
        print(f"[PosterX] Cleanup error in {folder}: {e}")

# --- دالة: حفظ الصورة ---
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
            return True
        return False
    except Exception as e:
        print(f"[PosterX] Save error: {e}")
        return False

# --- دالة: جلب بالـ TMDb ID ---
def _fetch_by_tmdb_id(self, tmdb_id, dwn_poster, media_type="movie"):
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={API_KEYS['tmdb_api']}&append_to_response=images,external_ids"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return False, f"[TMDb ID] HTTP {resp.status_code}"
        data = resp.json()

        if not data.get("title" if media_type == "movie" else "name"):
            return False, "[TMDb ID] No title found"

        basename = convtext(data.get("title") or data.get("name") or "Unknown")
        base_folder = os.path.dirname(dwn_poster)

        # --- تنزيل البوستر ---
        if data.get("poster_path"):
            url_poster_img = f"https://image.tmdb.org/t/p/{poster_size}{data['poster_path']}"
            self.savePoster(dwn_poster, url_poster_img)

        # --- تنزيل الباكدروب ---
        if data.get("backdrop_path"):
            backdrop_file = os.path.join(FOLDERS["backdrop"], f"{basename}_backdrop.jpg")
            url_backdrop = f"https://image.tmdb.org/t/p/{backdrop_size}{data['backdrop_path']}"
            self.savePoster(backdrop_file, url_backdrop)

        # --- جلب من Fanart.tv ---
        tvdb_id = data.get("external_ids", {}).get("tvdb_id") if media_type == "tv" else None
        self._fetch_from_fanarttv(int(tmdb_id), tvdb_id, media_type, base_folder, basename)

        return True, f"[TMDb ID OK] {tmdb_id}"

    except Exception as e:
        return False, f"[TMDb ID Error] {str(e)}"

# --- الفئة الرئيسية ---
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

            # --- التحقق من وجود ID في الوصف ---
            imdb_match = re.search(r'tt\d{7,8}', fulldesc)
            tmdb_match = re.search(r'tmdb[:\s]+(\d+)', fulldesc, re.I)
            thetvdb_match = re.search(r'tvdb[:\s]+(\d+)', fulldesc, re.I)

            if tmdb_match:
                return self._fetch_by_tmdb_id(int(tmdb_match.group(1)), dwn_poster, "movie")
            elif thetvdb_match:
                return self._fetch_from_thetvdb(dwn_poster, title, year)

            # --- استخراج السنة ---
            year_match = re.search(r'\b(19|20)\d{2}\b', fd)
            year = year_match.group(0) if year_match else None

            # --- تحديد النوع ---
            if any(word in fd.lower() for word in ["film", "movie", "фильм", "кино", "cinema"]):
                srch = "movie"
            elif any(word in fd.lower() for word in ["series", "episode", "staffel", "série", "сериал", "серия", "tv"]):
                srch = "tv"

            # --- جلب من TMDb ---
            success, log = self._fetch_from_tmdb(dwn_poster, title, year, srch, fd)
            if success:
                return True, log

            # --- تحليل اسم الملف إذا فشل ---
            if not success and channel:
                rec_title, rec_year = extract_title_year_from_filename(title)
                if rec_title:
                    success, log = self._fetch_from_tmdb(dwn_poster, rec_title, rec_year, srch, fd)
                    if success:
                        return True, log

            # --- المصادر البديلة ---
            if API_KEYS.get('fallback_sources', True):
                if 'tv' in srch or 'series' in fd.lower():
                    success, log = self._fetch_from_thetvdb(dwn_poster, title, year)
                    if success:
                        return True, log
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

            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return False, f"[TMDb] HTTP {resp.status_code}"
            data = resp.json()

            if not data.get("results"):
                return False, "[TMDb] No results"

            result = data["results"][0]
            media_id = result["id"]
            media_type = result.get("media_type", srch)
            poster_path = result.get("poster_path")

            base_folder = os.path.dirname(dwn_poster)
            basename = os.path.splitext(os.path.basename(dwn_poster))[0]

            # --- تنزيل البوستر ---
            if poster_path:
                url_poster_img = f"https://image.tmdb.org/t/p/{poster_size}{poster_path}"
                self.savePoster(dwn_poster, url_poster_img)

            # --- جلب التفاصيل الكاملة ---
            details_url = f"https://api.themoviedb.org/3/{media_type}/{media_id}?api_key={API_KEYS['tmdb_api']}&append_to_response=images,external_ids"
            details_resp = requests.get(details_url, timeout=10)
            if details_resp.status_code != 200:
                return True, f"[TMDb OK] {title} (No details)"

            details = details_resp.json()

            # --- 1. Backdrop ---
            if details.get("backdrop_path"):
                backdrop_file = os.path.join(FOLDERS["backdrop"], f"{basename}_backdrop.jpg")
                url_backdrop = f"https://image.tmdb.org/t/p/{backdrop_size}{details['backdrop_path']}"
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

            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return
            data = resp.json()

            # --- Logo (PNG) ---
            if data.get("hdmovielogo"):
                logo_file = os.path.join(FOLDERS["logo"], f"{basename}_logo.png")
                self.savePoster(logo_file, data["hdmovielogo"][0]["url"])
            elif data.get("hdtvlogo"):
                logo_file = os.path.join(FOLDERS["logo"], f"{basename}_logo.png")
                self.savePoster(logo_file, data["hdtvlogo"][0]["url"])

            # --- Banner ---
            if data.get("moviebanner"):
                banner_file = os.path.join(FOLDERS["banner"], f"{basename}_banner.jpg")
                self.savePoster(banner_file, data["moviebanner"][0]["url"])
            elif data.get("tvbanner"):
                banner_file = os.path.join(FOLDERS["banner"], f"{basename}_banner.jpg")
                self.savePoster(banner_file, data["tvbanner"][0]["url"])

            # --- Fanart (خلفية عالية الجودة) ---
            if data.get("moviethumb") or data.get("moviebackground"):
                fanart_list = data.get("moviethumb") or data.get("moviebackground")
                if fanart_list:
                    fanart_file = os.path.join(FOLDERS["backdrop"], f"{basename}_fanart.jpg")
                    self.savePoster(fanart_file, fanart_list[0]["url"])

        except Exception as e:
            print(f"[Fanart.tv] Error: {e}")

    def _fetch_from_thetvdb(self, dwn_poster, title, year):
        try:
            if not API_KEYS.get('thetvdb_api'):
                return False, "[TheTVDB] No API Key"

            headers = {
                "Authorization": f"Bearer {API_KEYS['thetvdb_api']}",
                "Content-Type": "application/json"
            }
            url = f"https://api4.thetvdb.com/v4/search?query={quote(title)}&type=series"
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code != 200:
                return False, f"[TheTVDB] Auth Failed ({resp.status_code})"

            data = resp.json()
            if not data.get("data"):
                return False, "[TheTVDB] No results"

            series_id = data["data"][0]["id"]
            details_url = f"https://api4.thetvdb.com/v4/series/{series_id}"
            details = requests.get(details_url, headers=headers, timeout=10).json()

            if not details.get("data"):
                return False, "[TheTVDB] No details"

            # --- جلب الصورة ---
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
            query = quote(f"{title} movie tv poster")
            url = f"https://www.google.com/search?q={query}&tbm=isch&tbs=ift:jpg,isz:m"
            resp = requests.get(url, headers=headers, timeout=10).text

            # البحث عن أول صورة
            match = re.search(r'\],\["https://([^"]+\.jpe?g)"', resp)
            if match:
                img_url = "https://" + match.group(1).split("&")[0]
                if "googleusercontent" not in img_url and "gstatic" not in img_url:
                    self.savePoster(dwn_poster, img_url)
                    return True, f"[Google OK] {title}"

            return False, "[Google] Not found"

        except Exception as e:
            return False, f"[Google Error] {e}"

    def savePoster(self, dwn_poster, url_poster):
        savePoster(self, dwn_poster, url_poster)

    def _fetch_by_tmdb_id(self, tmdb_id, dwn_poster, media_type="movie"):
        return _fetch_by_tmdb_id(self, tmdb_id, dwn_poster, media_type)