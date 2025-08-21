# -*- coding: utf-8 -*-
# TN_PosterX.py - by digiteng & your-helper
# ريندر احترافي لجلب البوسترات من TMDB, TVDB, Fanart.tv, OMDb
# <widget source="session.Event_Now" render="TN_PosterX" nexts="1" position="..." size="..." />

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, eEPGCache
from Components.Sources.Event import Event
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
import NavigationInstance
import os
import re
import time
from threading import Thread

# --- إصلاح جوهري: تعريف epgcache ---
epgcache = eEPGCache.getInstance()

# --- دالة التسجيل ---
LOG_FILE = "/media/hdd/logs/TN_PosterX.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tn_log("=== TN_PosterX تم تحميل الريندر ===")

# --- إعدادات اللغة ---
try:
    from Components.config import config
    lng = config.osd.language.value.split("_")[0]  # مثل: "ar", "en", "fr"
    tn_log(f"[CONFIG] اللغة: {lng}")
except:
    lng = "en"
    tn_log("[CONFIG] اللغة: en (افتراضي)")

# --- تحديد المسار الرئيسي ---
base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TNPosterX"
poster_folder = ""

tn_log("[PATH] بدء البحث عن مجلد مناسب...")
for path in base_paths:
    if os.path.exists(path):
        test_path = os.path.join(path, base_folder)
        if os.access(path, os.W_OK):
            poster_folder = os.path.join(test_path, "poster")
            os.makedirs(poster_folder, exist_ok=True)
            tn_log(f"[PATH] تم استخدام: {poster_folder}")
            break
        else:
            tn_log(f"[PATH] لا صلاحيات كتابة في: {path}")
    else:
        tn_log(f"[PATH] المسار غير موجود: {path}")

if not poster_folder:
    poster_folder = "/tmp/TNPosterX/poster"
    os.makedirs(poster_folder, exist_ok=True)
    tn_log(f"[PATH] استخدام المسار الافتراضي: {poster_folder}")

# --- تنظيف اسم الحدث ---
REGEX = re.compile(
    r'([\(\[]).*?([\)\]])|'
    r': odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|'
    r'\|\s[0-9]+\+|[0-9]+\+|'
    r'\s\d{4}\Z|'
    r'([\(\[\|].*?[\)\]\|])|'
    r'(\"|\"\.|\"\,|\.)\s.+|'
    r'\"|:|\*|'
    r'Премьера\.\s|'
    r'(х|Х|м|М|т|Т|д|Д)/ф\s|'
    r'(х|Х|м|М|т|Т|д|Д)/с\s|'
    r'\s(с|С)(езон|ерия|-н|-я)\s.+|'
    r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
    r'\.\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
    r'\s(ч|ч\.|с\.|с)\s\d{1,3}.+|'
    r'\d{1,3}(-я|-й|\sс-н).+|'
    r'ح\s*\d+|'
    r'الجزء\s*\d+|'
    r'الحلقة\s*\d+|'
    r'Episode\s*\d+|'
    r'Part\s*\d+|'
    r'S\d+E\d+|'
    r'\s-\sS\d+|'
    , re.DOTALL | re.IGNORECASE)

def clean_title(title):
    if not title:
        tn_log("[CLEAN] عنوان فارغ")
        return ""
    cleaned = re.sub(REGEX, '', title).strip()
    tn_log(f"[CLEAN] '{title}' → '{cleaned}'")
    return cleaned

# --- صف التنزيل ---
try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=20)
tn_log("[QUEUE] صف التنزيل جاهز")

# --- استيراد خيط التنزيل ---
try:
    from .TN_PosterXDownload import TNPosterXDownloader
    downloader = TNPosterXDownloader(poster_folder, lng)
    tn_log("[DOWNLOADER] تم تحميل TN_PosterXDownload.py")
except Exception as e:
    tn_log(f"[ERROR] فشل تحميل Downloader: {e}")
    downloader = None

class TN_PosterX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nexts = 0
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)
        self.filename = ""
        tn_log("[INIT] TN_PosterX تم تهيئة")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nexts":
                self.nexts = int(value)
                tn_log(f"[SKIN] nexts={self.nexts}")
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[CHANGED] what={what}")
        if not self.instance:
            tn_log("[CHANGED] instance غير متوفر")
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            tn_log("[CHANGED] CHANGED_CLEAR - تم الإخفاء")
            return

        try:
            service = None
            if isinstance(self.source, Event):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                tn_log(f"[SOURCE] نوع المصدر: Event → {service}")
            elif hasattr(self.source, "getCurrentService"):
                service = self.source.getCurrentService()
                tn_log(f"[SOURCE] نوع المصدر: CurrentService → {service}")
            elif hasattr(self.source, "getServiceRef"):
                service = self.source.getServiceRef()
                tn_log(f"[SOURCE] نوع المصدر: ServiceRef → {service}")

            if not service:
                tn_log("[SERVICE] لا يوجد service")
                self.instance.hide()
                return

            # --- البحث عن الأحداث ---
            events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, self.nexts + 1, -1)])
            tn_log(f"[EPG] عدد الأحداث المتاحة: {len(events)}")
            if len(events) <= self.nexts:
                tn_log(f"[EPG] لا يوجد حدث {self.nexts}")
                self.instance.hide()
                return

            evt = events[self.nexts]
            title = evt[4] or ""
            short_desc = evt[5] or ""
            full_desc = evt[6] or ""
            tn_log(f"[EVENT] الحدث {self.nexts}: {title}")

            clean_name = clean_title(title)
            if not clean_name:
                tn_log("[EVENT] الاسم النظيف فارغ")
                self.instance.hide()
                return

            self.filename = os.path.join(poster_folder, f"{clean_name}.jpg")
            tn_log(f"[FILE] مسار الحفظ: {self.filename}")

            # --- التحقق من الكاش ---
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                tn_log(f"[CACHE] بوستر موجود في الكاش")
                self.timer.start(1, True)
            else:
                tn_log(f"[QUEUE] إضافة إلى الصف للتنزيل: {title}")
                download_queue.put({
                    "title": title,
                    "short": short_desc,
                    "full": full_desc,
                    "filename": self.filename,
                    "lang": lng
                })
                if downloader and not downloader.is_alive():
                    tn_log("[THREAD] تشغيل خيط التنزيل")
                    downloader.start()
                self.wait_and_show()

        except Exception as e:
            tn_log(f"[ERROR] خطأ في changed: {e}")
            self.instance.hide()

    def showPoster(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[SHOW] عرض البوستر: {self.filename}")
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()
        else:
            tn_log("[SHOW] لا يمكن العرض - ملف غير موجود أو فارغ")
            self.instance.hide()

    def wait_and_show(self):
        timer = eTimer()
        timer.callback.append(self.check_and_show)
        timer.start(200, True)

    def check_and_show(self):
        for _ in range(15):  # انتظر 3 ثواني
            time.sleep(0.2)
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                tn_log(f"[CHECK] البوستر جاهز: {self.filename}")
                self.timer.start(1, True)
                return
        tn_log("[CHECK] انتهت المحاولة - لم يتم التنزيل")
        self.instance.hide()