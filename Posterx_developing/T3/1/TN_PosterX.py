# -*- coding: utf-8 -*-
# TN_PosterX.py - by digiteng & your-helper
# ريندر لجلب البوسترات من TMDB, TVDB, OMDb, Fanart.tv
# <widget source="session.Event_Now" render="TN_PosterX" nexts="1" ... />

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Components.Sources.Event import Event
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from enigma import eEPGCache
import NavigationInstance
import os
import re
import time
from threading import Thread

# --- إعدادات اللغة ---
try:
    from Components.config import config
    lng = config.osd.language.value.split("_")[0]  # "en", "ar", "fr"
except:
    lng = "en"

# --- تحديد المسار الرئيسي ---
base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TNPosterX"
poster_folder = ""

for path in base_paths:
    if os.path.ismount(path) or path == "/tmp":
        test_path = os.path.join(path, base_folder)
        if os.access(path, os.W_OK):
            poster_folder = os.path.join(test_path, "poster")
            os.makedirs(poster_folder, exist_ok=True)
            break

if not poster_folder:
    # كحل أخير
    poster_folder = "/tmp/TNPosterX/poster"
    os.makedirs(poster_folder, exist_ok=True)

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
    r'\s(س|С)(езон|ерия|-н|-я)\s.+|'
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
        return ""
    return re.sub(REGEX, '', title).strip()

# --- صف التنزيل ---
try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=20)

# --- استيراد خيط التنزيل ---
try:
    from .TN_PosterXDownload import TNPosterXDownloader
    downloader = TNPosterXDownloader(poster_folder, lng)
except Exception as e:
    print(f"[TN_PosterX] خطأ في تحميل Downloader: {e}")
    downloader = None

class TN_PosterX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nexts = 0
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)
        self.filename = ""

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nexts":
                self.nexts = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        try:
            service = None
            if isinstance(self.source, Event):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
            elif hasattr(self.source, "getCurrentService"):
                service = self.source.getCurrentService()
            elif hasattr(self.source, "getServiceRef"):
                service = self.source.getServiceRef()

            if not service:
                self.instance.hide()
                return

            events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, self.nexts + 1, -1)])
            if len(events) <= self.nexts:
                self.instance.hide()
                return

            evt = events[self.nexts]
            title = evt[4] or ""
            short_desc = evt[5] or ""
            full_desc = evt[6] or ""

            clean_name = clean_title(title)
            if not clean_name:
                self.instance.hide()
                return

            self.filename = os.path.join(poster_folder, f"{clean_name}.jpg")

            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.timer.start(1, True)
            else:
                # إضافة إلى الصف
                download_queue.put({
                    "title": title,
                    "short": short_desc,
                    "full": full_desc,
                    "filename": self.filename,
                    "lang": lng
                })
                # تشغيل الخيط
                if downloader and not downloader.is_alive():
                    downloader.start()
                # انتظار عرض
                self.wait_and_show()

        except Exception as e:
            print(f"[TN_PosterX] خطأ: {e}")
            self.instance.hide()

    def showPoster(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()
        else:
            self.instance.hide()

    def wait_and_show(self):
        timer = eTimer()
        timer.callback.append(self.check_and_show)
        timer.start(200, True)

    def check_and_show(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.timer.start(1, True)
        else:
            # حاول مرة أخرى بعد 300 مللي ثانية، حتى 10 مرات
            for _ in range(10):
                time.sleep(0.3)
                if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                    self.timer.start(1, True)
                    return
            self.instance.hide()