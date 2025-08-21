# -*- coding: utf-8 -*-
from .TN_Requests import SESSION
from .TN_Utils import extract_series_info, log, CONFIG
import re

TMDB_API = "3c3efcf47c3577558812bb9d64019d65"
FANART_API = "6d231536dea4318a88cb2520ce89473b"

def search_tmdb(query, media_type="multi", year=None, language="ar"):
    try:
        url = f"https://api.themoviedb.org/3/search/{media_type}"
        params = {'api_key': TMDB_API, 'query': query, 'language': language}
        if year:
            params['year'] = year
        resp = SESSION.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            return results[0] if results else None
    except Exception as e:
        log(f"[TN_lib] TMDb search error: {e}")
    return None

def get_tmdb_data(tmdb_id, media_type, language="ar"):
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
        params = {
            'api_key': TMDB_API,
            'append_to_response': 'images,external_ids',
            'language': language
        }
        resp = SESSION.get(url, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        log(f"[TN_lib] TMDb data error: {e}")
        return None

def get_fanarttv(tmdb_id=None, tvdb_id=None, media_type="movie"):
    try:
        if media_type == "movie" and tmdb_id:
            url = f"https://webservice.fanart.tv/v3/movies/{tmdb_id}"
        elif tvdb_id:
            url = f"https://webservice.fanart.tv/v3/tv/{tvdb_id}"
        else:
            return None
        headers = {"api_key": FANART_API}
        resp = SESSION.get(url, headers=headers, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        log(f"[TN_lib] Fanart.tv error: {e}")
        return None

def find_by_imdb_id(imdb_id, media_type="movie", language="ar"):
    try:
        url = f"https://api.themoviedb.org/3/find/{imdb_id}"
        params = {
            'api_key': TMDB_API,
            'external_source': 'imdb_id',
            'language': language
        }
        resp = SESSION.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if media_type == "movie":
                return data.get("movie_results", [None])[0]
            else:
                return data.get("tv_results", [None])[0]
    except Exception as e:
        log(f"[TN_lib] IMDb find error: {e}")
    return None

def verify_match(result, year, event_type_hint=None):
    if year:
        release_year = result.get("release_date", "")[:4] if result.get("release_date") else None
        if release_year and year != release_year:
            log(f"[Verify] Year mismatch: {year} vs {release_year}")
            return False
    if event_type_hint:
        if event_type_hint == "movie" and not result.get("title"):
            return False
        if event_type_hint == "series" and not result.get("name"):
            return False
    return True

def search_movie_smart(title, year=None, shortdesc="", fulldesc=""):
    log(f"[Search] Starting smart search for: {title}")
    
    # --- 1. جلب عبر IMDb ID ---
    imdb_match = re.search(r'tt\d{7,8}', fulldesc)
    if imdb_match:
        result = find_by_imdb_id(imdb_match.group(0), "movie")
        if result:
            log(f"[Search] Found by IMDb ID: {imdb_match.group(0)}")
            return result

    # --- 2. جلب عبر TMDb ID ---
    tmdb_match = re.search(r'tmdb[:\s]+(\d+)', fulldesc, re.I)
    if tmdb_match:
        data = get_tmdb_data(int(tmdb_match.group(1)), "movie")
        if data:
            log(f"[Search] Found by TMDb ID: {tmdb_match.group(1)}")
            return data

    # --- 3. استخراج معلومات السلسلة ---
    clean_title, is_movie_part, part_num, season, episode = extract_series_info(title)

    # --- 4. أولًا: جرب العنوان الأصلي ---
    result = search_tmdb(title, "movie", year, CONFIG['language'])
    if result and verify_match(result, year):
        log(f"[Search] Found by full title: {title}")
        return result

    # --- 5. إذا كان فيلم جزء، ابحث في السلسلة ---
    if is_movie_part:
        collection = search_tmdb(f"{clean_title} Collection", "movie")
        if collection and collection.get("belongs_to_collection"):
            coll_id = collection["belongs_to_collection"]["id"]
            url = f"https://api.themoviedb.org/3/collection/{coll_id}"
            params = {'api_key': TMDB_API, 'language': 'en'}
            resp = SESSION.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                coll_data = resp.json()
                for movie in coll_data.get("parts", []):
                    if str(movie.get("title")).lower() == title.lower():
                        log(f"[Search] Found part in collection: {title}")
                        return movie
                    if movie.get("title", "").startswith(clean_title) and str(part_num) in movie.get("title", ""):
                        return movie

    # --- 6. جرب بالاسم النظيف ---
    result = search_tmdb(clean_title, "movie", year, CONFIG['language'])
    if result and verify_match(result, year):
        return result

    # --- 7. جرب باللغات الداعمة ---
    for lang in CONFIG['search_languages'].split(','):
        result = search_tmdb(clean_title, "movie", year, lang.strip())
        if result and verify_match(result, year):
            log(f"[Search] Found using language {lang}: {clean_title}")
            return result

    return None