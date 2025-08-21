# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
import os
import re
import time

DEBUG = True
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
            tn_log(f"[PATH] تم استخدام: {test_path}")
            break
        except Exception as e:
            tn_log(f"[PATH] فشل في {path}: {e}")
else:
    fallback = "/tmp/TN_X"
    for folder in ["poster", "backdrop", "logo", "banner", "rating", "cast", "cache"]:
        folders[folder] = os.path.join(fallback, folder)
        os.makedirs(folders[folder], exist_ok=True)
    tn_log(f"[PATH] استخدام المسار الافتراضي: {fallback}")

try:
    from .TN_XTools import clean_title
except:
    REGEX = re.compile(r'[\(\[].*?[\)\]]|:\s*odc\.\s*\d+|S\d+\s*-\s*E\d+|S\d+|E\d+|\s*-\s*S\d+|\s*-\s*Episode\s*\d+|\s*-\s*Part\s*\d+|\s*-\s*ح\s*\d+|\s*-\s*الحلقة\s*\d+|\s*-\s*الجزء\s*\d+|\s*\d+\s*odc|\s*-\s*\d+|\s*\(\w+\)|\s*\[.*?\]|\s*-\s*[^-\s]+$|\s*\(?\d{4}\)?|\s*-\s*-\s*', re.IGNORECASE | re.DOTALL)
    def clean_title(title):
        if not title: return ""
        cleaned = re.sub(REGEX, '', title).strip()
        return re.sub(r'\s+', ' ', cleaned)

try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=10)
pending_requests = set()
downloader = None
_active_renderers = []

def on_item_downloaded(clean_name):
    tn_log(f"[NOTIFY] تم تنزيل كل بيانات: {clean_name}")
    for renderer in list(_active_renderers):
        try:
            if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
                if renderer.instance:
                    ext = ".png" if renderer.type == "logo" else ".jpg"
                    file_path = os.path.join(folders[renderer.type], f"{clean_name}{ext}")
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        tn_log(f"[NOTIFY] تحديث renderer: {clean_name} (type: {renderer.type})")
                        renderer.showContent()
                else:
                    tn_log(f"[NOTIFY] تجاهل renderer بدون instance: {clean_name}")
        except Exception as e:
            tn_log(f"[NOTIFY] خطأ في تحديث renderer: {e}")

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
        self.type = "poster"
        self.nextEvent = 0
        self.nxEvntUsed = "poster"  # poster, backdrop, banner
        self.epgcache = eEPGCache.getInstance()
        self.timer = eTimer()
        self.timer.callback.append(self.showPicture)
        self.filename = ""
        self.clean_name = ""
        if self not in _active_renderers:
            _active_renderers.append(self)
        tn_log(f"[INIT] TN_X تم تهيئة")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == "type":
                self.nxEvntUsed = value.lower()
            elif attrib == "nextEvent":
                self.nextEvent = int(value)
            elif attrib == "size":
                self.piconsize = value
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
            return
        if what[0] != self.CHANGED_CLEAR:
            self.instance.hide()
            self.timer.start(100, True)
        else:
            self.instance.hide()

    def showPicture(self):
        try:
            ref = self.source.service
            if not ref:
                self.instance.hide()
                return

            events = self.epgcache.lookupEvent(['T', (ref.toString(), 0, -1, 10)])
            tn_log(f"[EPGCACHE] عدد الأحداث: {len(events) if events else 0}")
            if not events or len(events) <= self.nextEvent:
                self.instance.hide()
                return

            title = events[self.nextEvent][0]
            self.clean_name = clean_title(title)
            tn_log(f"[EPGCACHE] تم جلب الحدث رقم {self.nextEvent}: {title}")

            folder_map = {
                "poster": folders["poster"],
                "backdrop": folders["backdrop"],
                "banner": folders["banner"]
            }
            ext = ".jpg"
            self.filename = os.path.join(folder_map.get(self.nxEvntUsed, folders["poster"]), f"{self.clean_name}{ext}")

            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.instance.setPixmapFromFile(self.filename)
                self.instance.show()
            else:
                self.instance.hide()

                if self.filename in pending_requests:
                    tn_log(f"[PENDING] طلب مكرر - تخطي: {self.clean_name}")
                    return

                if download_queue.full():
                    try:
                        download_queue.get_nowait()
                    except:
                        pass

                download_queue.put({
                    "title": title,
                    "short": "",
                    "full": "",
                    "clean_name": self.clean_name,
                    "langs": ["en"]
                })
                pending_requests.add(self.filename)

        except Exception as e:
            tn_log(f"[ERROR] showPicture: {e}")
            self.instance.hide()