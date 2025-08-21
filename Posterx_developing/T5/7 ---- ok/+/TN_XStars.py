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
    pathLoc = "/tmp/TN_X/rating"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

REGEX_CLEAN = re.compile(
    r'[\(\[].*?[\)\]]|'
    r':\s*odc\.\s*\d+|'
    r'S\d+\s*-\s*E\d+|'
    r'S\d+|E\d+|'
    r'\s*-\s*S\d+|'
    r'\s*-\s*Episode\s*\d+|'
    r'\s*-\s*Part\s*\d+|'
    r'\s*-\s*ح\s*\d+|'
    r'\s*-\s*الحلقة\s*\d+|'
    r'\s*-\s*الجزء\s*\d+|'
    r'\s*\d+\s*odc|'
    r'\s*-\s*\d+|'
    r'\s*\(\w+\)|'
    r'\s*\[.*?\]|'
    r'\s*-\s*[^-\s]+$|'
    r'\s*\(?\d{4}\)?|'
    r'\s*-\s*-\s*',
    re.IGNORECASE | re.DOTALL
)

RATING_TO_STARS = {
    "G": 100, "TV-G": 100, "U": 100,
    "PG": 40, "TV-PG": 40, "PG-13": 60,
    "TV-14": 60, "TV-12": 50, "TV-10": 40,
    "TV-Y7": 30, "TV-Y": 20,
    "R": 80, "TV-MA": 80, "NR": 80, "15": 70, "12A": 50,
    "": 0, "Not Rated": 0, "Unrated": 0, "N/A": 0
}

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.clean_name = ""
        tn_log("=== TN_XStars تم تهيئة ===")

    GUI_WIDGET = eSlider

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((1,))

    def changed(self, what):
        tn_log(f"[STARS] تم استدعاء changed: {what}")
        if not self.instance:
            return

        try:
            event = None
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
            else:
                tn_log("[STARS] لا يمكن جلب الحدث")
                self.value = 0
                return

            if not event:
                self.value = 0
                return

            title = event.getEventName()
            self.clean_name = re.sub(REGEX_CLEAN, '', title).strip()
            tn_log(f"[STARS] الاسم النظيف: {self.clean_name}")

            rating_file = os.path.join(pathLoc, f"{self.clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    content = f.read().strip()
                    tn_log(f"[STARS] محتوى التقييم: '{content}'")

                    try:
                        rating = float(content)
                        self.value = int(rating * 10)
                    except ValueError:
                        self.value = RATING_TO_STARS.get(content, 0)
            else:
                tn_log(f"[STARS] ملف التقييم غير موجود: {rating_file}")
                self.value = 0

        except Exception as e:
            tn_log(f"[STARS] خطأ: {e}")
            self.value = 0