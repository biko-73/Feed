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

try:
    from Components.config import config
    lng = config.osd.language.value.split("_")[0]
except:
    lng = "en"

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
            break
        except:
            pass

try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=10)
pending_requests = set()
downloader = None
active_renderers = []

def on_item_downloaded(clean_name):
    tn_log(f"[NOTIFY] تم تنزيل كل بيانات: {clean_name}")
    for renderer in active_renderers:
        if hasattr(renderer, "clean_name") and renderer.clean_name == clean_name:
            ext = ".png" if renderer.type == "logo" else ".jpg"
            file_path = os.path.join(folders[renderer.type], f"{clean_name}{ext}")
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                tn_log(f"[NOTIFY] تحديث renderer: {clean_name} (type: {renderer.type})")
                renderer.showContent()

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

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "type":
                self.type = value.lower()
        return Renderer.applySkin(self, desktop, parent)

    def get_search_languages(self, title):
        if re.search(r'[\u0600-\u06FF]', title):
            return ['ar', 'en', 'fr', 'de', 'es', 'it', 'pl', 'pt', 'ru', 'cs', 'tr']
        elif re.search(r'[ąćęłńóśźż]', title):
            return ['pl', 'en', 'de', 'cs', 'tr', 'ru', 'fr', 'it', 'pt', 'ar']
        elif re.search(r'[çğıöşü]', title):
            return ['tr', 'en', 'de', 'fr', 'ar', 'pl', 'ru', 'cs', 'it', 'pt']
        elif re.search(r'[šđčćž]', title):
            return ['cs', 'en', 'de', 'tr', 'ru', 'fr', 'pl', 'it', 'pt', 'ar']
        elif re.search(r'[ëË]', title):
            return ['sq', 'en', 'tr', 'it', 'fr', 'de', 'pl']
        else:
            return ['en', 'ar', 'fr', 'de', 'es', 'it', 'pl', 'pt', 'ru', 'cs', 'tr']

    def changed(self, what):
        tn_log(f"[CHANGED] what={what}")
        if not self.instance:
            return

        try:
            event = None
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
            else:
                source_str = str(self.source)
                if "Event[" in source_str:
                    import re
                    match = re.search(r"Event\[(\d+)\]", source_str)
                    if match:
                        index = int(match.group(1))
                        from NavigationInstance import navigation
                        service_ref = navigation.getCurrentlyPlayingServiceReference()
                        if service_ref:
                            from enigma import eEPGCache
                            epg = eEPGCache.getInstance()
                            events = epg.lookupEvent(['RIBDT', (service_ref.toString(), 0, -1)])
                            if events and len(events) > index:
                                event_data = events[index]
                                from enigma import eServiceEvent
                                evt = eServiceEvent()
                                evt.m_event_name = event_data[4] or ""
                                event = evt

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

            clean_name = re.sub(r'([\(\[]).*?([\)\]])|: odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|\*|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|م|М|т|Т|د|Д)/с\s|\s(س|С)(езон|ерия|-ن|-я)\s.+|\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\.\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\s(ч|ч\.|س\.|س)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|ح\s*\d+|الجزء\s*\d+|الحلقة\s*\d+|Episode\s*\d+|Part\s*\d+|S\d+E\d+|\s-\sS\d+|\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|\b(Episode|Épisode|Folge)\s*\d+|\b(Temporada|Série)\s*\d+|\b(Serija|Epizoda)\s*\d+|\b(серія|эпізод)\s*\d+|\b(серия|эпизод)\s*\d+|\b(Filma|Film)\s*\d+|\b(الحلقة|الموسم|الجزء)\s*\d+|\b(حلقة|موسم|جزء)\s*\d+|\b(مسلسل|فيلم|برنامج)\s+|\b(يعرض الآن|الحلقة القادمة)|\b(بالعربية|HD|1080|720)|\b(مترجم|مدبلج)|', '', title, flags=re.DOTALL | re.IGNORECASE).strip()
            clean_name = re.sub(r'\s+', ' ', clean_name)

            folder_map = {
                "poster": folders["poster"],
                "backdrop": folders["backdrop"],
                "logo": folders["logo"],
                "banner": folders["banner"]
            }
            ext = ".png" if self.type == "logo" else ".jpg"
            self.filename = os.path.join(folder_map.get(self.type, folders["poster"]), f"{clean_name}{ext}")

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

            tn_log(f"[QUEUE] إضافة للتنزيل: {title} (type: {self.type})")
            pending_requests.add(self.filename)

            langs = self.get_search_languages(title)
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
                "clean_name": clean_name,
                "langs": unique_langs
            })

            if downloader is None or not downloader.is_alive():
                start_downloader()

            self.wait_and_show()

        except Exception as e:
            tn_log(f"[ERROR] خطأ: {e}")
            self.instance.hide()

    def showContent(self):
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            self.instance.setPixmapFromFile(self.filename)
            self.instance.setScale(1)
            self.instance.show()

    def wait_and_show(self):
        self.check_and_show(0)

    def check_and_show(self, retry):
        if retry > 60:
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