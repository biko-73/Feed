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
    r'\s\d{1,3}\s(ч|ч\.|с\.|س)\s.+|'
    r'\.\s\d{1,3}\s(ч|ч\.|с\.|س)\s.+|'
    r'\s(ч|ч\.|س\.|س)\s\d{1,3}.+|'
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
parental_renderers = []
stars_renderers = []

def on_item_downloaded(clean_name):
    tn_log(f"[NOTIFY] تم تنزيل كل بيانات: {clean_name}")
    # تحديث TN_X
    for renderer in active_renderers:
        if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
            ext = ".png" if renderer.type == "logo" else ".jpg"
            file_path = os.path.join(folders[renderer.type], f"{clean_name}{ext}")
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                tn_log(f"[NOTIFY] تحديث renderer: {clean_name} (type: {renderer.type})")
                renderer.showContent()
    # تحديث TN_XParental
    for renderer in parental_renderers:
        if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
            tn_log(f"[NOTIFY] تحديث TN_XParental: {clean_name}")
            renderer.showContent()
    # تحديث TN_XStars
    for renderer in stars_renderers:
        if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
            tn_log(f"[NOTIFY] تحديث TN_XStars: {clean_name}")
            renderer.changed((1,))

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
        self.timer = eTimer()
        self.timer.callback.append(self.showContent)
        self.filename = ""
        self.current_event_id = None
        self.clean_name = ""
        if self not in active_renderers:
            active_renderers.append(self)
        tn_log(f"[INIT] TN_X تم تهيئة")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "type":
                self.type = value.lower()
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[CHANGED] what={what}")
        if not self.instance:
            return

        try:
            event = None

            # 1. الحدث الحالي
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
                tn_log("[SOURCE] تم جلب الحدث من self.source.event")

            # 2. Event_Now / Event_Next
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
                tn_log("[SOURCE] تم جلب الحدث من getCurrentEvent()")

            # 3. دعم Event[2], Event[3], ... عبر eEPGCache
            else:
                try:
                    source_str = str(self.source)
                    if "Event[" in source_str:
                        import re
                        match = re.search(r"Event\[(\d+)\]", source_str)
                        if match:
                            index = int(match.group(1))
                            tn_log(f"[EVENT_INDEX] محاولة جلب الحدث رقم: {index}")

                            service_ref = None
                            if hasattr(self.source, "getCurrentService"):
                                service_ref = self.source.getCurrentService()
                            else:
                                from NavigationInstance import navigation
                                service_ref = navigation.getCurrentlyPlayingServiceReference()

                            if service_ref:
                                from enigma import eEPGCache
                                epg = eEPGCache.getInstance()
                                events = epg.lookupEvent(['RIBDT', (service_ref.toString(), 0, -1)])
                                tn_log(f"[EPGCACHE] تم جلب {len(events)} حدثًا من EPG")

                                if events and len(events) > index:
                                    event_data = events[index]
                                    title = event_data[4] or ""
                                    begin = event_data[2]
                                    event_id = event_data[1]
                                    tn_log(f"[EVENT_INDEX] تم جلب الحدث: {title}")

                                    from enigma import eServiceEvent
                                    evt = eServiceEvent()
                                    evt.m_event_name = title
                                    evt.m_start_time = begin
                                    event = evt
                                else:
                                    tn_log(f"[EVENT_INDEX] لا يوجد حدث عند index={index}")
                            else:
                                tn_log("[EVENT_INDEX] لا يمكن جلب service_ref")
                except Exception as e:
                    tn_log(f"[EVENT_INDEX] خطأ: {e}")

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

            tn_log(f"[QUEUE] إضافة للتنزيل: {title} (type: {self.type})")
            pending_requests.add(self.filename)
            download_queue.put({
                "title": title,
                "short": short,
                "full": full,
                "clean_name": self.clean_name,
                "langs": [lng, "ar", "en", "fr", "de", "es", "it", "pl", "pt", "ru", "cs", "tr"]
            })

            if downloader is None or not downloader.is_alive():
                tn_log("[THREAD] إعادة تشغيل الخيط")
                start_downloader()

            self.wait_and_show()

        except Exception as e:
            tn_log(f"[ERROR] خطأ: {e}")
            self.instance.hide()

    def showContent(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[SHOW] عرض: {self.filename}")
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()
        else:
            tn_log("[SHOW] لا يمكن العرض")
            self.instance.hide()

    def wait_and_show(self):
        self.check_and_show(0)

    def check_and_show(self, retry):
        if retry > 60:
            tn_log("[CHECK] انتهت المحاولة")
            self.instance.hide()
            return
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[CHECK] الملف جاهز: {self.filename}")
            self.timer.start(1, True)
        else:
            timer = eTimer()
            timer.callback.append(lambda: self.check_and_show(retry + 1))
            timer.start(50, True)

    def __del__(self):
        if self in active_renderers:
            active_renderers.remove(self)
        tn_log("[DEL] TN_X تم تدميره")