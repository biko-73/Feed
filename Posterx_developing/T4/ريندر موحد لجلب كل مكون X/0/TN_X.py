# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Components.Sources.Event import Event
import os
import re
import time

DEBUG = False
LOG_FILE = "/media/hdd/logs/TN_X.log"

def tn_log(txt):
    if not DEBUG:
        return
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tn_log("=== TN_X تم تحميل الريندر ===")

try:
    from Components.config import config
    lng = config.osd.language.value.split("_")[0]
except:
    lng = "en"
tn_log(f"[CONFIG] اللغة: {lng}")

base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TN_X"
folders = {}

for path in base_paths:
    if os.path.exists(path) and os.access(path, os.W_OK):
        test_path = os.path.join(path, base_folder)
        try:
            for folder in ["poster", "backdrop", "logo", "banner", "rating", "cast", "cache"]:
                folders[folder] = os.path.join(test_path, folder)
                os.makedirs(folders[folder], exist_ok=True)
            tn_log(f"[PATH] تم إنشاء المجلدات في: {test_path}")
            break
        except:
            continue
else:
    base_path = "/tmp/TN_X"
    for folder in ["poster", "backdrop", "logo", "banner", "rating", "cast", "cache"]:
        folders[folder] = os.path.join(base_path, folder)
        os.makedirs(folders[folder], exist_ok=True)
    tn_log(f"[PATH] استخدام المسار الافتراضي: {base_path}")

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
    r'\s(س|С)(езон|ерия|-ن|-я)\s.+|'
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
    r'\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|'
    r'\b(Episode|Épisode|Folge)\s*\d+|'
    r'\b(Temporada|Série)\s*\d+|'
    r'\b(Serija|Epizoda)\s*\d+|'
    r'\b(серія|эпізод)\s*\d+|'
    r'\b(серия|эпизод)\s*\d+|'
    r'\b(Filma|Film)\s*\d+|'
    r'\b(الحلقة|الموسم|الجزء)\s*\d+|'
    r'\b(حلقة|موسم|جزء)\s*\d+|'
    r'\b(مسلسل|فيلم|برنامج)\s+|'
    r'\b(يعرض الآن|الحلقة القادمة)|'
    r'\b(بالعربية|HD|1080|720)|'
    r'\b(مترجم|مدبلج)|'
    , re.DOTALL | re.IGNORECASE)

ARABIC_KEYWORDS = [
    "الحلقة", "الموسم", "الجزء", "مترجم", "مدبلج", "مباشر", "بث حي",
    "يعرض الآن", "الحلقة القادمة", "مسلسل", "فيلم", "برنامج", "عرض خاص",
    "مكرر", "مجدول", "مباشرة", "جودة عالية", "HD", "FHD", "UHD"
]

def clean_title(title):
    if not title:
        return ""
    cleaned = title
    for word in ARABIC_KEYWORDS:
        cleaned = re.sub(rf'\b{word}\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(REGEX, '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned

try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=10)
pending_requests = set()
downloader = None
active_renderers = []

def on_item_downloaded(filename):
    tn_log(f"[NOTIFY] تم التنزيل: {filename}")
    for renderer in active_renderers:
        if renderer.filename == filename:
            renderer.showPoster()

def start_downloader():
    global downloader
    try:
        from .TN_XDownload import TN_X_Downloader
        downloader = TN_X_Downloader(
            download_queue=download_queue,
            folders=folders,
            lng=lng,
            pending_requests=pending_requests,
            on_download_complete=on_item_downloaded
        )
        downloader.daemon = True
        downloader.start()
        tn_log("[DOWNLOADER] تم تشغيل الخيط")
    except Exception as e:
        tn_log(f"[ERROR] فشل تحميل Downloader: {e}")

start_downloader()

class TN_X(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nexts = 0
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)
        self.filename = ""
        self.current_event_id = None
        if self not in active_renderers:
            active_renderers.append(self)

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nexts":
                self.nexts = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
            return
        try:
            event = self.source.event
            if not event:
                self.instance.hide()
                return
            title = event.getEventName() or ""
            short = event.getShortDescription() or ""
            full = event.getExtendedDescription() or ""
            event_id = event.getEventId()
            if event_id == self.current_event_id:
                return
            self.current_event_id = event_id
            clean_name = clean_title(title)
            if not clean_name:
                self.instance.hide()
                return
            self.filename = os.path.join(folders["poster"], f"{clean_name}.jpg")
            self.instance.hide()
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.timer.start(1, True)
                return
            if self.filename in pending_requests:
                return
            if download_queue.full():
                try:
                    download_queue.get_nowait()
                except:
                    pass
            pending_requests.add(self.filename)
            download_queue.put({
                "title": title,
                "short": short,
                "full": full,
                "clean_name": clean_name,
                "langs": [lng, "ar", "en", "fr", "de", "es", "it", "pl", "cs", "pt", "ru"]
            })
            if downloader is None or not downloader.is_alive():
                start_downloader()
            self.wait_and_show()
        except Exception as e:
            tn_log(f"[ERROR] {e}")
            self.instance.hide()

    def showPoster(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()
        else:
            self.instance.hide()

    def wait_and_show(self):
        self.check_and_show(0)

    def check_and_show(self, retry):
        if retry > 30:
            self.instance.hide()
            return
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.timer.start(1, True)
        else:
            timer = eTimer()
            timer.callback.append(lambda: self.check_and_show(retry + 1))
            timer.start(50, True)

    def __del__(self):
        if self in active_renderers:
            active_renderers.remove(self)