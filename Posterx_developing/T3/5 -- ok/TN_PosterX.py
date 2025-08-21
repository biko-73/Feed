# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Components.Sources.Event import Event
from Components.Sources.ServiceEvent import ServiceEvent
import os
import re
import time

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
    lng = config.osd.language.value.split("_")[0]
    tn_log(f"[CONFIG] اللغة: {lng}")
except:
    lng = "en"
    tn_log("[CONFIG] اللغة: en")

# --- تحديد المسار ---
base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TNPosterX"
poster_folder = ""

for path in base_paths:
    if os.path.exists(path) and os.access(path, os.W_OK):
        test_path = os.path.join(path, base_folder)
        poster_folder = os.path.join(test_path, "poster")
        os.makedirs(poster_folder, exist_ok=True)
        tn_log(f"[PATH] تم استخدام: {poster_folder}")
        break
else:
    poster_folder = "/tmp/TNPosterX/poster"
    os.makedirs(poster_folder, exist_ok=True)
    tn_log(f"[PATH] استخدام المسار الافتراضي: {poster_folder}")

# --- تنظيف الاسم ---
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
    return re.sub(REGEX, '', title).strip() if title else ""

# --- صف التنزيل ---
try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=20)
tn_log("[QUEUE] صف التنزيل جاهز")

# --- تعريف downloader كمتغير عالمي ---
downloader = None

# --- استيراد الخيط ---
def start_downloader():
    global downloader
    try:
        from .TN_PosterXDownload import TNPosterXDownloader
        downloader = TNPosterXDownloader(poster_folder, lng)
        downloader.daemon = True
        downloader.start()
        tn_log("[DOWNLOADER] تم تشغيل الخيط")
    except Exception as e:
        tn_log(f"[ERROR] فشل تحميل Downloader: {e}")

# --- تشغيل الخيط أول مرة ---
start_downloader()

class TN_PosterX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nexts = 0
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)
        self.filename = ""
        self.current_event_id = None
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
            return

        try:
            event = self.source.event
            if not event:
                tn_log("[EVENT] لا يوجد حدث")
                self.instance.hide()
                return

            # --- تحديد الحدث ---
            if self.nexts == 0:
                evt = event
            else:
                service = None
                try:
                    service = self.source.getCurrentService()
                except:
                    pass
                if service:
                    from enigma import eEPGCache
                    events = eEPGCache.getInstance().lookupEvent(['IBDCTESX', (service.toString(), 0, self.nexts + 1, -1)])
                    if len(events) > self.nexts:
                        evt = events[self.nexts]
                    else:
                        self.instance.hide()
                        return
                else:
                    self.instance.hide()
                    return

            title = evt.getEventName() or ""
            short = evt.getShortDescription() or ""
            full = evt.getExtendedDescription() or ""

            # --- تجنب التكرار ---
            event_id = evt.getEventId()
            if event_id == self.current_event_id:
                tn_log("[DUPLICATE] نفس الحدث - تخطي")
                return
            self.current_event_id = event_id

            clean_name = clean_title(title)
            if not clean_name:
                tn_log("[CLEAN] الاسم فارغ")
                self.instance.hide()
                return

            self.filename = os.path.join(poster_folder, f"{clean_name}.jpg")
            tn_log(f"[FILE] المسار: {self.filename}")

            # --- إخفاء أولًا ---
            self.instance.hide()

            # --- عرض من الكاش إن وُجد ---
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                tn_log(f"[CACHE] عرض من الكاش: {self.filename}")
                self.timer.start(1, True)
            else:
                # --- إضافة إلى الصف ---
                tn_log(f"[QUEUE] إضافة للتنزيل: {title}")
                download_queue.put({
                    "title": title,
                    "short": short,
                    "full": full,
                    "filename": self.filename,
                    "lang": lng
                })
                # --- إعادة تشغيل الخيط إذا مات ---
                global downloader
                if downloader is None or not downloader.is_alive():
                    tn_log("[THREAD] إعادة تشغيل الخيط")
                    start_downloader()
                self.wait_and_show()

        except Exception as e:
            tn_log(f"[ERROR] خطأ: {e}")
            self.instance.hide()

    def showPoster(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[SHOW] عرض: {self.filename}")
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()
        else:
            tn_log("[SHOW] لا يمكن العرض")
            self.instance.hide()

    def wait_and_show(self):
        timer = eTimer()
        timer.callback.append(lambda: self.check_and_show(0))
        timer.start(50, True)

    def check_and_show(self, retry):
        if retry > 20:
            self.instance.hide()
            return
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.timer.start(1, True)
        else:
            timer = eTimer()
            timer.callback.append(lambda: self.check_and_show(retry + 1))
            timer.start(50, True)