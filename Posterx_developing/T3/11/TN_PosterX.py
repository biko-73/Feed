# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Components.Sources.Event import Event
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

# --- صف التنزيل ---
try:
    from queue import Queue
except:
    from Queue import Queue

download_queue = Queue(maxsize=5)
tn_log("[QUEUE] صف التنزيل جاهز (maxsize=5)")

# --- قائمة بالطلبات المضافة ---
pending_requests = set()

# --- تعريف downloader كمتغير عالمي ---
downloader = None

# --- قائمة بالريندرز النشطة ---
active_renderers = []

# --- دالة استدعاء عند اكتمال التنزيل ---
def on_poster_downloaded(filename):
    tn_log(f"[NOTIFY] تم التنزيل: {filename}")
    for renderer in active_renderers:
        if renderer.filename == filename:
            tn_log(f"[NOTIFY] تحديث renderer: {filename}")
            renderer.showPoster()

# --- استيراد الخيط (متأخر) ---
def start_downloader():
    global downloader
    try:
        from .TN_PosterXDownload import TNPosterXDownloader
        downloader = TNPosterXDownloader(
            download_queue=download_queue,
            poster_folder=poster_folder,
            lng=lng,
            pending_requests=pending_requests,
            on_download_complete=on_poster_downloaded
        )
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
        active_renderers.append(self)
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

            # --- جلب الحدث حسب nexts ---
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
                return

            # --- منع التكرار ---
            if self.filename in pending_requests:
                tn_log(f"[PENDING] طلب مكرر - تخطي: {clean_name}")
                return

            # --- إضافة إلى الصف فقط إذا لم يكن ممتلئًا ---
            if download_queue.full():
                tn_log("[QUEUE] الصف ممتلئ - إزالة عنصر قديم")
                try:
                    download_queue.get_nowait()
                except:
                    pass

            tn_log(f"[QUEUE] إضافة للتنزيل: {title}")
            pending_requests.add(self.filename)
            download_queue.put({
                "title": title,
                "short": short,
                "full": full,
                "filename": self.filename,
                "langs": [lng, "ar", "en", "fr", "de", "es", "it", "pl", "cs", "pt", "ru"]
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
        self.check_and_show(0)

    def check_and_show(self, retry):
        if retry > 30:
            tn_log("[CHECK] انتهت المحاولة")
            self.instance.hide()
            return
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            tn_log(f"[CHECK] البوستر جاهز: {self.filename}")
            self.timer.start(1, True)
        else:
            timer = eTimer()
            timer.callback.append(lambda: self.check_and_show(retry + 1))
            timer.start(50, True)

    def __del__(self):
        if self in active_renderers:
            active_renderers.remove(self)
        tn_log("[DEL] TN_PosterX تم تدميره")