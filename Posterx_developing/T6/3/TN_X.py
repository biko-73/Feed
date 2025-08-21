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

# قائمة آمنة للتحديثات
_active_renderers = []

def on_item_downloaded(clean_name):
    tn_log(f"[NOTIFY] تم تنزيل كل بيانات: {clean_name}")
    # نسخ القائمة لتجنب التغيير أثناء التكرار
    for renderer in list(_active_renderers):
        try:
            if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
                # تأكد أن instance لا يزال موجودًا وصالحًا
                if renderer.instance and renderer.instance.valid():
                    ext = ".png" if renderer.type == "logo" else ".jpg"
                    file_path = os.path.join(folders[renderer.type], f"{clean_name}{ext}")
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        tn_log(f"[NOTIFY] تحديث renderer: {clean_name} (type: {renderer.type})")
                        renderer.showContent()
                else:
                    tn_log(f"[NOTIFY] تجاهل renderer ميت: {clean_name}")
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
        self.timer = eTimer()
        self.timer.callback.append(self.showContent)
        self.filename = ""
        self.current_event_id = None
        self.clean_name = ""
        # أضف إلى القائمة الآمنة
        if self not in _active_renderers:
            _active_renderers.append(self)
        tn_log(f"[INIT] TN_X تم تهيئة")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "type":
                self.type = value.lower()
            elif attr == "nextEvent":
                self.nextEvent = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[CHANGED] what={what}")
        if not self.instance:
            return

        try:
            event = None

            if hasattr(self.source, "service"):
                try:
                    ref = self.source.service
                    if ref:
                        from enigma import eEPGCache
                        epg = eEPGCache.getInstance()
                        events = epg.lookupEvent(['T', (ref.toString(), 0, -1, 10)])
                        if events and len(events) > self.nextEvent:
                            title = events[self.nextEvent][0]
                            from enigma import eServiceEvent
                            evt = eServiceEvent()
                            evt.m_event_name = title
                            event = evt
                            tn_log(f"[EPGCACHE] تم جلب الحدث رقم {self.nextEvent}: {title}")
                except Exception as e:
                    tn_log(f"[EPGCACHE] خطأ: {e}")

            if not event:
                tn_log("[EVENT] لا يوجد حدث")
                self.instance.hide()
                return

            title = event.getEventName() or ""
            short = event.getShortDescription() or ""
            full = event.getExtendedDescription() or ""

            event_id = event.getEventId()
            if event_id == self.current_event_id:
                tn_log("[DUPLICATE] نفس الحدث - تخطي")
                return
            self.current_event_id = event_id

            self.clean_name = clean_title(title)
            if not self.clean_name:
                tn_log("[CLEAN] الاسم فارغ")
                self.instance.hide()
                return

            folder_map = {
                "poster": folders["poster"],
                "backdrop": folders["backdrop"],
                "logo": folders["logo"],
                "banner": folders["banner"]
            }
            ext = ".png" if self.type == "logo" else ".jpg"
            self.filename = os.path.join(folder_map.get(self.type, folders["poster"]), f"{self.clean_name}{ext}")

            self.instance.hide()

            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                tn_log(f"[CACHE] عرض من الكاش: {self.filename}")
                self.timer.start(1, True)
                return

            if self.filename in pending_requests:
                tn_log(f"[PENDING] طلب مكرر - تخطي: {self.clean_name}")
                return

            if download_queue.full():
                tn_log("[QUEUE] الصف ممتلئ - إزالة عنصر قديم")
                try:
                    download_queue.get_nowait()
                except:
                    pass

            tn_log(f"[QUEUE] إضافة للتنزيل: {title} (type: {self.type}, nextEvent: {self.nextEvent})")
            pending_requests.add(self.filename)

            langs = ['ar', 'en']  # ترتيب البحث
            seen_langs = set()
            unique_langs = []
            for lang in langs:
                if lang not in seen_langs:
                    seen_langs.add(lang)
                    unique_langs.append(lang)
            tn_log(f"[LANG] ترتيب البحث: {unique_langs}")

            download_queue.put({
                "title": title,
                "short": short,
                "full": full,
                "clean_name": self.clean_name,
                "langs": unique_langs
            })

            if downloader is None or not downloader.is_alive():
                tn_log("[THREAD] إعادة تشغيل الخيط")
                start_downloader()

            self.wait_and_show()

        except Exception as e:
            tn_log(f"[ERROR] خطأ: {e}")
            self.instance.hide()

    def showContent(self):
        try:
            if self.instance and self.instance.valid() and os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.instance.setPixmapFromFile(self.filename)
                self.instance.setScale(1)
                self.instance.show()
            else:
                self.instance.hide()
        except:
            self.instance.hide()

    def wait_and_show(self):
        self.check_and_show(0)

    def check_and_show(self, retry):
        if retry > 60:
            tn_log("[CHECK] انتهت المحاولة")
            self.instance.hide()
            return
        try:
            if self.instance and self.instance.valid() and os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                tn_log(f"[CHECK] الملف جاهز: {self.filename}")
                self.timer.start(1, True)
            else:
                timer = eTimer()
                timer.callback.append(lambda: self.check_and_show(retry + 1))
                timer.start(50, True)
        except:
            self.instance.hide()

    def __del__(self):
        try:
            if self in _active_renderers:
                _active_renderers.remove(self)
            tn_log("[DEL] TN_X تم تدميره")
        except:
            pass