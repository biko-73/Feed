# -*- coding: utf-8 -*-
import re
import unicodedata
import os
import time
from configparser import ConfigParser

# --- تحميل الإعدادات ---
def load_config():
    config = {
        'language': 'ar',
        'search_languages': 'fr,en,es,de,tr,ru,it',
        'quality': 'HD',
        'max_storage_mb': 2048,
        'fallback_sources': True
    }
    try:
        cfg = ConfigParser()
        if os.path.exists("/etc/enigma2/PosterX.conf"):
            if hasattr(cfg, 'read_file'):
                with open("/etc/enigma2/PosterX.conf") as f:
                    cfg.read_file(f)
            else:
                cfg.read("/etc/enigma2/PosterX.conf")
            if cfg.has_section('SETTINGS'):
                for key in config:
                    if cfg.has_option('SETTINGS', key):
                        val = cfg.get('SETTINGS', key)
                        if key == 'max_storage_mb':
                            config[key] = int(val)
                        elif key == 'fallback_sources':
                            config[key] = val.lower() == 'true'
                        else:
                            config[key] = val
    except:
        pass
    return config

CONFIG = load_config()

# --- تنظيف النص ---
def convtext(text):
    if not text:
        return ""
    # إزالة HTML entities
    text = re.sub(r'&#[0-9]+;', '', text)
    # الحفاظ على الأرقام للجزء/الحلقة
    text = re.sub(r'\b(BluRay|WEB-DL|مترجم|جودة عالية|Uncensored|Extended|AC3|DTS)\b', '', text, flags=re.I)
    text = re.sub(r'[\|\[\]\(\)\_\-\:]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    except:
        pass
    return text.upper()

# --- استخراج الجزء/الحلقة ---
def extract_series_info(title):
    if not title:
        return title, False, None, None, None

    original = title
    is_movie_part = False
    part_number = None
    season = None
    episode = None

    # --- 1. استخراج رقم الجزء ---
    part_match = re.search(r'\b(part|الجزء|الجزء|الجزء)\s*(\d+)', title, re.I)
    if part_match:
        part_number = int(part_match.group(2))
        is_movie_part = True

    direct_part = re.search(r'(?:^|[\s_\(\[])(\d+)(?:\s*(?:part|الجزء|الجزء|الجزء)?)(?:$|[\s_\)\]])', title)
    if direct_part and 2 <= int(direct_part.group(1)) <= 10:
        part_number = int(direct_part.group(1))
        is_movie_part = True

    # --- 2. استخراج الموسم والحلقة ---
    s_match = re.search(r's(\d{1,2})e(\d{1,3})', title, re.I)
    if s_match:
        season = int(s_match.group(1))
        episode = int(s_match.group(2))

    ep_match = re.search(r'(?:episode|حلقة|حلقه|ep)\s*(\d+)', title, re.I)
    if ep_match:
        episode = int(ep_match.group(1))

    # --- 3. تنظيف الاسم مع الحفاظ على الهوية ---
    clean_title = re.sub(r'\b(part|الجزء|الجزء|الجزء)\s*\d+', '', title, flags=re.I)
    clean_title = re.sub(r's\d+e\d+', '', clean_title, flags=re.I)
    clean_title = re.sub(r'(?:episode|حلقة|حلقه|ep)\s*\d+', '', clean_title, flags=re.I)
    clean_title = re.sub(r'\(\d+\)', '', clean_title)
    clean_title = re.sub(r'[\[\]\(\)_\-]+', ' ', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()

    return clean_title, is_movie_part, part_number, season, episode

# --- تحديد الذاكرة ---
def get_external_storage():
    for path in ['/media/hdd', '/media/usb', '/tmp']:
        if os.path.exists(path) and os.access(path, os.W_OK):
            return path
    return '/tmp'

# --- إنشاء المجلدات ---
def setup_folders(base_path="TN_X"):
    root = os.path.join(get_external_storage(), base_path)
    folders = {
        "poster": os.path.join(root, "Poster_X"),
        "backdrop": os.path.join(root, "backdrops_X"),
        "banner": os.path.join(root, "banners_X"),
        "logo": os.path.join(root, "logos_X")
    }
    for folder in folders.values():
        os.makedirs(folder, exist_ok=True)
    log_file = os.path.join(root, "TNPosterX.log")
    return folders, log_file

# --- تسجيل الأخطاء ---
def log(msg):
    try:
        with open(setup_folders()[1], "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass