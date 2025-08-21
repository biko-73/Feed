# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re

try:
    # جلب المسارات من TN_X.py
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    # احتياطي: استخدام /tmp/infos إذا فشل الاستيراد
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
    r'(х|Х|м|М|т|Т|д|Д)/с\s|'
    r'\s(س|С)(езон|ерия|-ن|-я)\s.+|'
    r'\s\d{1,3}\s(ч|ч\.|с\.|с)\s.+|'
    r'\.\s\d{1,3}\s(ч|ч\.|с\.|س)\s.+|'
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

    GUI_WIDGET = eSlider

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.value = 0
            return

        try:
            event = None
            if hasattr(self.source, "event"):
                event = self.source.event
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
            else:
                return

            if not event:
                self.value = 0
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    try:
                        rating = float(f.read().strip())
                        self.value = int(rating * 10)  # 0-100
                    except:
                        self.value = 0
            else:
                self.value = 0
        except:
            self.value = 0

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def getRange(self):
        return 0, 100

    range = property(getRange, lambda self, range: None)