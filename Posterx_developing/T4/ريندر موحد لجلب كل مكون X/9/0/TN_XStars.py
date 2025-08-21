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
REGEX = re.compile(r'([\(\[]).*?([\)\]])|: odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|\*|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|м|М|т|Т|д|Д)/с\s|\s(س|С)(езон|ерия|-н|-я)\s.+|\s\d{1,3}\s(ч|ч\.|с\.|س)\s.+|\.\s\d{1,3}\s(ч|ч\.|с\.|س)\s.+|\s(ч|ч\.|س\.|س)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|ح\s*\d+|الجزء\s*\d+|الحلقة\s*\d+|Episode\s*\d+|Part\s*\d+|S\d+E\d+|\s-\sS\d+|\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|\b(Episode|Épisode|Folge)\s*\d+|\b(Temporada|Série)\s*\d+|\b(Serija|Epizoda)\s*\d+|\b(серія|эпізод)\s*\d+|\b(серия|эпизод)\s*\d+|\b(Filma|Film)\s*\d+|\b(الحلقة|الموسم|الجزء)\s*\d+|\b(حلقة|موسم|جزء)\s*\d+|\b(مسلسل|فيلم|برنامج)\s+|\b(يعرض الآن|الحلقة القادمة)|\b(بالعربية|HD|1080|720)|\b(مترجم|مدبلج)|', re.DOTALL | re.IGNORECASE)

# --- خريطة التقييمات إلى نجوم ---
RATING_TO_STARS = {
    "G": 100, "TV-G": 100,
    "PG": 40, "TV-PG": 40, "PG-13": 60,
    "TV-14": 60, "TV-12": 50, "TV-10": 40,
    "TV-Y7": 30, "TV-Y": 20,
    "R": 80, "TV-MA": 80,
    "": 0, "Not Rated": 0, "Unrated": 0, "N/A": 0
}

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
                    content = f.read().strip()
                    # إذا كان رقمًا (مثل 8.5)
                    try:
                        rating = float(content)
                        self.value = int(rating * 10)  # 0-100
                    except ValueError:
                        # إذا كان نصًا (مثل TV-14)
                        stars = RATING_TO_STARS.get(content, 0)
                        self.value = stars
            else:
                self.value = 0
        except Exception as e:
            self.value = 0

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)