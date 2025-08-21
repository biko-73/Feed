# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re
import json
import os

# المسار الثابت للملف
MAPPING_FILE = "/media/hdd/TN_X/titles_map.json"

REGEX_CLEAN = re.compile(
    r'[\(\[].*?[\)\]]|'
    r':\s*odc\.\s*\d+|'
    r'S\d+\s*-\s*E\d+|'
    r'S\d+|E\d+|'
    r'\s*-\s*S\d+|'
    r'\s*-\s*Episode\s*\d+|'
    r'\s*-\s*Part\s*\d+|'
    r'\s*-\s*ح\s*\d+|'
    r'\s*-\s*الحلقة\s*\d+|'
    r'\s*-\s*الجزء\s*\d+|'
    r'\s*\d+\s*odc|'
    r'\s*-\s*\d+|'
    r'\s*\(\w+\)|'
    r'\s*\[.*?\]|'
    r'\s*-\s*[^-\s]+$|'
    r'\s*\(?\d{4}\)?|'
    r'\s*-\s*-\s*',
    re.IGNORECASE | re.DOTALL
)

def clean_title(title):
    if not title:
        return ""
    cleaned = re.sub(REGEX_CLEAN, '', title).strip()
    return re.sub(r'\s+', ' ', cleaned)

def load_mapping():
    """قراءة الخريطة من ملف JSON"""
    if os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("TITLE_MAPPING", {}), data.get("NO_IMAGE_NAMES", [])
        except Exception as e:
            print(f"[TN_XTools] خطأ في قراءة الملف: {e}")
    return {}, []

def save_mapping(title_mapping, no_image_names):
    """حفظ الخريطة إلى ملف JSON"""
    try:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "TITLE_MAPPING": title_mapping,
                "NO_IMAGE_NAMES": no_image_names
            }, f, ensure_ascii=False, indent=4)
        print(f"[TN_XTools] تم حفظ الخريطة إلى {MAPPING_FILE}")
    except Exception as e:
        print(f"[TN_XTools] خطأ في حفظ الملف: {e}")

def auto_update_mapping(title, clean_name):
    """
    تحديث الخريطة تلقائيًا عند نجاح TMDB
    """
    title_mapping, no_image_names = load_mapping()

    # لا تُضف الأسماء العامة
    ignore_keywords = ["برنامج", "قناة", "عرض", "JOURNAL", "FIN", "Pause", "Zakończenie"]
    if any(keyword in title for keyword in ignore_keywords):
        return

    # أضف التحويل إذا لم يكن موجودًا
    if title not in title_mapping and clean_name:
        title_mapping[title] = clean_name
        save_mapping(title_mapping, no_image_names)
        print(f"[TN_XTools] تم إضافة تطابق جديد: '{title}' → '{clean_name}'")