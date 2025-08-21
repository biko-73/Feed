# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    pathLoc = "/tmp/infos/"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

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
    r'(х|Х|м|М|т|Т|د|Д)/с\s|'
    r'\s(س|С)(езون|ерия|-ن|-я)\s.+|'
    r'\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|'
    r'\.\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|'
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

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        tn_log("=== TN_XStars تم تحميله ===")

    GUI_WIDGET = eSlider

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "pixmap":
                self.__pixmap = value
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[STARS] CHANGED: what={what}")
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.value = 0
            tn_log("[STARS] تم تغيير: CLEAR")
            return

        try:
            event = None
            if hasattr(self.source, "event"):
                event = self.source.event
                tn_log(f"[STARS] تم جلب الحدث: {event.getEventName()}")
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
                tn_log(f"[STARS] تم جلب الحدث من getCurrentEvent: {event.getEventName()}")
            else:
                tn_log("[STARS] لا يمكن جلب الحدث")
                return

            if not event:
                self.value = 0
                tn_log("[STARS] الحدث فارغ")
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()
            tn_log(f"[STARS] الاسم النظيف: {clean_name}")

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                tn_log(f"[STARS] تم العثور على ملف التقييم: {rating_file}")
                with open(rating_file, "r") as f:
                    content = f.read().strip()
                    tn_log(f"[STARS] محتوى الملف: {content}")
                    try:
                        rating = float(content)
                        self.value = int(rating * 10)
                        tn_log(f"[STARS] تم عرض التقييم: {rating}")
                    except:
                        self.value = 0
                        tn_log("[STARS] فشل تحويل التقييم إلى رقم")
            else:
                tn_log(f"[STARS] لم يوجد ملف التقييم: {rating_file}")
                self.value = 0
        except Exception as e:
            tn_log(f"[STARS] خطأ: {e}")
            self.value = 0

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def getRange(self):
        return 0, 100

    range = property(getRange, lambda self, range: None)