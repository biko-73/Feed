# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider, ePixmap
import os
import re

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    pathLoc = "/tmp/infos/"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

REGEX = re.compile(r'([\(\[]).*?([\)\]])|: odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|\*|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|м|М|ت|Т|د|د)/س\s|\s(س|С)(езон|ерия|-ن|-я)\s.+|\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\.\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\s(ч|ч\.|س\.|س)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|ح\s*\d+|الجزء\s*\d+|الحلقة\s*\d+|Episode\s*\d+|Part\s*\d+|S\d+E\d+|\s-\sS\d+|\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|\b(Episode|Épisode|Folge)\s*\d+|\b(Temporada|Série)\s*\d+|\b(Serija|Epizoda)\s*\d+|\b(серія|эпізод)\s*\d+|\b(серия|эпизод)\s*\d+|\b(Filma|Film)\s*\d+|\b(الحلقة|الموسم|الجزء)\s*\d+|\b(حلقة|موسم|جزء)\s*\d+|\b(مسلسل|فيلم|برنامج)\s+|\b(يعرض الآن|الحلقة القادمة)|\b(بالعربية|HD|1080|720)|\b(مترجم|مدبلج)|', re.DOTALL | re.IGNORECASE)

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.__pixmap = None
        self.__size = (100, 20)

    GUI_WIDGET = eSlider

    def applySkin(self, desktop, parent):
        # جلب قيمة pixmap من السكين
        for attr, value in self.skinAttributes:
            if attr == "pixmap":
                self.__pixmap = value
            elif attr == "size":
                try:
                    self.__size = tuple(map(int, value.split(",")))
                except:
                    pass
        return Renderer.applySkin(self, desktop, parent)

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