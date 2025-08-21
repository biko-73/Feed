# -*- coding: utf-8 -*-
import re
import unicodedata
import os

def convtext(text):
    if not text:
        return ""
    text = re.sub(r'&#[0-9]+;', '', text)
    text = re.sub(r'\b(1080p|720p|480p|BluRay|WEB-DL|مترجم|جودة عالية)\b', '', text, flags=re.I)
    text = re.sub(r'[\|\[\]\(\)\_\-\:]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    except:
        pass
    return text.upper()

def extract_title_year(filename):
    if not filename:
        return None, None
    year_match = re.search(r'\b(19|20)\d{2}\b', filename)
    year = year_match.group(0) if year_match else None
    clean_title = re.sub(r'\b(1080p|720p|BluRay|WEB-DL|مترجم)\b', '', filename, flags=re.I)
    clean_title = re.sub(r'[\.\_\-\(\)]+', ' ', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    if year:
        clean_title = re.sub(r'\b' + year + r'\b', '', clean_title)
    return clean_title.strip(), year

def get_external_storage():
    for path in ['/media/hdd', '/media/usb', '/tmp']:
        if os.path.exists(path) and os.access(path, os.W_OK):
            return path
    return '/tmp'

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
    return folders, os.path.join(root, "TNPosterX.log")