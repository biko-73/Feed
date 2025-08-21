# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re

# --- تحديد مسار rating ---
pathLoc = "/media/hdd/TN_X/rating"
if not os.path.exists(pathLoc):
    pathLoc = "/media/usb/TN_X/rating"
if not os.path.exists(pathLoc):
    pathLoc = "/tmp/TN_X/rating"
if not os.path.exists(pathLoc):
    os.makedirs(pathLoc)

# --- تنظيف العنوان ---
REGEX = re.compile(r'([\(\[]).*?([\)\]])|: odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|\*|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|м|М|ت|Т|د|Д)/с\s|\s(س|С)(езон|ерия|-н|-я)\s.+|\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\.\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\s(ч|ч\.|س\.|س)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|ح\s*\d+|الجزء\s*\d+|الحلقة\s*\d+|Episode\s*\d+|Part\s*\d+|S\d+E\d+|\s-\sS\d+|\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|\b(Episode|Épisode|Folge)\s*\d+|\b(Temporada|Série)\s*\d+|\b(Serija|Epizoda)\s*\d+|\b(серія|эпізод)\s*\d+|\b(серия|эпизод)\s*\d+|\b(Filma|Film)\s*\d+|\b(الحلقة|الموسم|الجزء)\s*\d+|\b(حلقة|موسم|جزء)\s*\d+|\b(مسلسل|فيلم|برنامج)\s+|\b(يعرض الآن|الحلقة القادمة)|\b(بالعربية|HD|1080|720)|\b(مترجم|مدبلج)|', re.DOTALL | re.IGNORECASE)

class TN_XStars(VariableValue, Renderer):
    GUI_WIDGET = eSlider

    def changed(self, what):
        if not self.instance:
            return
        try:
            # جلب الحدث
            event = None
            if hasattr(self.source, "event"):
                event = self.source.event
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
            else:
                self.value = 0
                return

            if not event:
                self.value = 0
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()

            # مسار الملف
            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    rating = f.read().strip()
                    try:
                        # تحويل النص إلى رقم (مثال: "8.5" -> 85)
                        self.value = int(float(rating) * 10)  # 0-100
                    except:
                        self.value = 0
            else:
                self.value = 0
        except:
            self.value = 0

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)