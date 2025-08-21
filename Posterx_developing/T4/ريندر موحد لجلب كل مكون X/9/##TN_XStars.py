# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re
import time

# --- إعدادات التعقب ---
DEBUG = True
LOG_FILE = "/media/hdd/logs/TN_X.log"

def tn_log(txt):
    if not DEBUG:
        return
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - [STARS] {txt}\n")
    except:
        pass

tn_log("=== TN_XStars تم تحميله ===")

# --- تحديد مسار rating ديناميكيًا ---
base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TN_X"
pathLoc = None

for path in base_paths:
    test_path = os.path.join(path, base_folder, "rating")
    if os.path.exists(test_path) and os.access(test_path, os.W_OK):
        pathLoc = test_path
        tn_log(f"[PATH] تم استخدام مسار rating: {pathLoc}")
        break

if pathLoc is None:
    fallback = "/tmp/infos/"
    if not os.path.exists(fallback):
        os.makedirs(fallback)
    pathLoc = fallback
    tn_log(f"[PATH] استخدام المسار الافتراضي: {pathLoc}")

# --- تنظيف العنوان ---
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

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        tn_log("TN_XStars: تم تهيئة")

    GUI_WIDGET = eSlider

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "pixmap":
                self.__pixmap = value
                tn_log(f"[SKIN] تم تعيين pixmap: {value}")
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"CHANGED: what={what}")
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.value = 0
            tn_log("[CLEAR] تم التنظيف")
            return

        try:
            event = None
            if hasattr(self.source, "event"):
                event = self.source.event
                tn_log(f"[SOURCE] تم جلب الحدث: {event.getEventName()}")
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
                tn_log(f"[SOURCE] تم جلب الحدث من getCurrentEvent: {event.getEventName()}")
            else:
                tn_log("[SOURCE] لا يمكن جلب الحدث")
                return

            if not event:
                self.value = 0
                tn_log("[EVENT] الحدث فارغ")
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()
            tn_log(f"[CLEAN] الاسم النظيف: {clean_name}")

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                tn_log(f"[FILE] تم العثور على الملف: {rating_file}")
                with open(rating_file, "r") as f:
                    content = f.read().strip()
                    tn_log(f"[CONTENT] محتوى الملف: '{content}'")
                    try:
                        # تحويل النص إلى رقم (مثال: "8.5" -> 85)
                        rating = float(content)
                        self.value = int(rating * 10)  # 0-100
                        tn_log(f"[VALUE] تم تعيين التقييم: {rating} -> {self.value}")
                    except ValueError:
                        tn_log("[ERROR] فشل تحويل التقييم إلى رقم")
                        self.value = 0
            else:
                tn_log(f"[MISSING] الملف غير موجود: {rating_file}")
                self.value = 0

        except Exception as e:
            tn_log(f"[EXCEPTION] خطأ غير متوقع: {e}")
            self.value = 0

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def getRange(self):
        return 0, 100

    range = property(getRange, lambda self, range: None)