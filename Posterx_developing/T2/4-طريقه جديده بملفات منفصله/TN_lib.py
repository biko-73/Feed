# -*- coding: utf-8 -*-
from .TN_Requests import SESSION
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
        params = {'api_key': TMDB_API, 'append_to_response': 'images,external_ids', 'language': language}
        resp = SESSION.get(url, params=params, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except:
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
    except:
        return None

def find_by_imdb_id(imdb_id, media_type="movie", language="ar"):
    try:
        url = f"https://api.themoviedb.org/3/find/{imdb_id}"
        params = {'api_key': TMDB_API, 'external_source': 'imdb_id', 'language': language}
        resp = SESSION.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("movie_results", [None])[0] if media_type == "movie" else data.get("tv_results", [None])[0]
    except:
        pass
    return None