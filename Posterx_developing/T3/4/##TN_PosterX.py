# -*- coding: utf-8 -*-
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
    lng = config.osd.language.value.split("_")[0]
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
        return ""
    return re.sub(REGEX, '', title).strip()

# --- صف التنزيل ---
try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=20)
tn_log("[QUEUE] صف التنزيل جاهز")

# --- دالة لإنشاء خيط جديد ---
def start_downloader():
    global downloader
    try:
        from .TN_PosterXDownload import TNPosterXDownloader
        downloader = TNPosterXDownloader()
        downloader.start()
        tn_log("[THREAD] تم إنشاء خيط تنزيل جديد")
    except Exception as e:
        tn_log(f"[ERROR] فشل إنشاء Downloader: {e}")

# --- خيط التنزيل ---
downloader = None
start_downloader()  # تشغيل خيط واحد يعيش طوال الوقت

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
                tn_log(f"[CACHE] بوستر موجود: {self.filename}")
                self.timer.start(1, True)  # أسرع عرض
            else:
                tn_log(f"[QUEUE] إضافة إلى الصف للتنزيل: {title}")
                download_queue.put({
                    "title": title,
                    "short": short_desc,
                    "full": full_desc,
                    "filename": self.filename,
                    "lang": lng
                })
                # لا نعيد إنشاء الخيط — نعتمد على الخيط الدائم
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
            tn_log("[SHOW] لا يمكن العرض - ملف غير موجود")
            self.instance.hide()

    def wait_and_show(self):
        # محاولة فورية بعد 100 مللي ثانية
        timer = eTimer()
        timer.callback.append(lambda: self.check_and_show(0))
        timer.start(100, True)

    def check_and_show(self, retry):
        if retry > 20:  # 2 ثانية كحد أقصى
            tn_log("[CHECK] انتهت المحاولة")
            self.instance.hide()
            return

        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[CHECK] البوستر جاهز: {self.filename}")
            self.timer.start(1, True)
        else:
            # تكرار كل 100 مللي ثانية
            timer = eTimer()
            timer.callback.append(lambda: self.check_and_show(retry + 1))
            timer.start(100, True)