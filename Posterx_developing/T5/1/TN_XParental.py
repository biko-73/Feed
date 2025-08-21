# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import re

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    pathLoc = "/tmp/TN_X/rating"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

curskin = "RED_DRAGON_FHD"
pratePath = f"/usr/share/enigma2/{curskin}/parental"

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

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        tn_log("=== TN_XParental تم تحميله ===")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "path":
                self.__path = value
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[PARENTAL] CHANGED: what={what}")
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            tn_log("[PARENTAL] تم تغيير: CLEAR")
            return

        try:
            event = None
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
            else:
                tn_log("[PARENTAL] لا يمكن جلب الحدث")
                return

            if not event:
                self.instance.hide()
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()
            tn_log(f"[PARENTAL] الاسم النظيف: {clean_name}")

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    rating = f.read().strip()
                    tn_log(f"[PARENTAL] التقييم: {rating}")

                    cert_map = {
                        "G": "0", "TV-G": "0",
                        "PG": "16", "TV-PG": "16", "PG-13": "16",
                        "TV-14": "14", "TV-12": "12", "TV-10": "10",
                        "TV-Y7": "6", "TV-Y": "6",
                        "R": "18", "TV-MA": "18", "NR": "18",
                        "": "UN", "Not Rated": "UN", "Unrated": "UN", "N/A": "UN"
                    }
                    cert = cert_map.get(rating, "UN")
                    fsk_path = f"/usr/share/enigma2/{self.__path}/FSK_{cert}.png"
                    tn_log(f"[PARENTAL] مسار الصورة: {fsk_path}")

                    if os.path.exists(fsk_path):
                        self.instance.setPixmapFromFile(fsk_path)
                        self.instance.show()
                    else:
                        self.instance.hide()
                        tn_log(f"[PARENTAL] الصورة غير موجودة: {fsk_path}")
            else:
                self.instance.hide()
                tn_log(f"[PARENTAL] ملف التقييم غير موجود: {rating_file}")
        except Exception as e:
            tn_log(f"[PARENTAL] خطأ: {e}")
            self.instance.hide()