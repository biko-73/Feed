# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
import os
import re
import time

# --- إعدادات ---
DEBUG = True
LOG_FILE = "/media/hdd/logs/TN_X.log"
pathLoc = "/media/hdd/TN_X/rating/"
if not os.path.exists(pathLoc):
    os.makedirs(pathLoc)

curskin = "GOLD_DRAGON_FHD"  # عدل حسب مظهرك
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
    r'(х|Х|م|М|т|Т|д|Д)/ф\s|'
    r'(х|Х|م|М|т|Т|д|Д)/с\s|'
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

def tn_log(txt):
    if not DEBUG:
        return
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - [PARENTAL] {txt}\n")
    except:
        pass

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        tn_log("تم تحميل TN_XParental")

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
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
                self.instance.hide()
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    rating = f.read().strip()
                    # تحويل التقييم إلى FSK
                    cert_map = {
                        "G": "0", "TV-G": "0",
                        "PG": "16", "TV-PG": "16", "PG-13": "16",
                        "TV-14": "14", "TV-12": "12", "TV-10": "10",
                        "TV-Y7": "6", "TV-Y": "6",
                        "R": "18", "TV-MA": "18",
                        "": "UN", "Not Rated": "UN", "Unrated": "UN", "N/A": "UN"
                    }
                    cert = cert_map.get(rating, "UN")
                    fsk_path = os.path.join(pratePath, f"FSK_{cert}.png")
                    if os.path.exists(fsk_path):
                        self.instance.setPixmapFromFile(fsk_path)
                        self.instance.show()
                    else:
                        self.instance.hide()
            else:
                self.instance.hide()
        except Exception as e:
            tn_log(f"خطأ: {e}")
            self.instance.hide()