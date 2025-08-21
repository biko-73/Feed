# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import re

# --- تأكد من استيراد المسار ---
try:
    from Components.Renderer.TN_X import folders
    pathLoc = folders["rating"]
except:
    pathLoc = "/tmp/TN_X/rating"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

curskin = "RED_DRAGON_FHD"
pratePath = f"/usr/share/enigma2/{curskin}/parental"

REGEX = re.compile(r'([\(\[]).*?([\)\]])|: odc\.\d+|\d+: odc\.\d+|\d+ odc\.\d+|:|!|/.*|\|\s[0-9]+\+|[0-9]+\+|\s\d{4}\Z|([\(\[\|].*?[\)\]\|])|(\"|\"\.|\"\,|\.)\s.+|\"|:|\*|Премьера\.\s|(х|Х|м|М|т|Т|д|Д)/ф\s|(х|Х|м|М|ت|Т|д|Д)/с\s|\s(س|С)(езон|ерия|-ن|-я)\s.+|\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\.\s\d{1,3}\s(ч|ч\.|س\.|س)\s.+|\s(ч|ч\.|س\.|س)\s\d{1,3}.+|\d{1,3}(-я|-й|\sс-н).+|ح\s*\d+|الجزء\s*\d+|الحلقة\s*\d+|Episode\s*\d+|Part\s*\d+|S\d+E\d+|\s-\sS\d+|\b(Saison|Season|Staffel|Serie|Episodio|Folge)\s*\d+|\b(Episode|Épisode|Folge)\s*\d+|\b(Temporada|Série)\s*\d+|\b(Serija|Epizoda)\s*\d+|\b(серія|эпізод)\s*\d+|\b(серия|эпизод)\s*\d+|\b(Filma|Film)\s*\d+|\b(الحلقة|الموسم|الجزء)\s*\d+|\b(حلقة|موسم|جزء)\s*\d+|\b(مسلسل|فيلم|برنامج)\s+|\b(يعرض الآن|الحلقة القادمة)|\b(بالعربية|HD|1080|720)|\b(مترجم|مدبلج)|', re.DOTALL | re.IGNORECASE)

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        tn_log("=== TN_XParental تم تحميله ===")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "path":
                self.__path = value
                tn_log(f"[PARENTAL] تم تعيين المسار: {self.__path}")
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[PARENTAL] CHANGED: what={what}")
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        try:
            event = None
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
                tn_log(f"[PARENTAL] حدث من self.source.event: {event.getEventName()}")
            elif hasattr(self.source, "getCurrentEvent"):
                event = self.source.getCurrentEvent()
                tn_log(f"[PARENTAL] حدث من getCurrentEvent: {event.getEventName() if event else 'None'}")
            else:
                tn_log("[PARENTAL] لا يمكن جلب الحدث من المصدر")
                return

            if not event:
                self.instance.hide()
                return

            title = event.getEventName()
            clean_name = re.sub(REGEX, '', title).strip()
            tn_log(f"[PARENTAL] الاسم النظيف: {clean_name}")

            rating_file = os.path.join(pathLoc, f"{clean_name}.txt")
            if os.path.exists(rating_file):
                tn_log(f"[PARENTAL] تم العثور على: {rating_file}")
                with open(rating_file, "r") as f:
                    rating = f.read().strip()
                    tn_log(f"[PARENTAL] التقييم المقروء: '{rating}'")

                    cert_map = {
                        "G": "0", "TV-G": "0",
                        "PG": "16", "TV-PG": "16", "PG-13": "16",
                        "TV-14": "14", "TV-12": "12", "TV-10": "10",
                        "TV-Y7": "6", "TV-Y": "6",
                        "R": "18", "TV-MA": "18", "NR": "18",
                        "": "UN", "Not Rated": "UN", "Unrated": "UN", "N/A": "UN"
                    }
                    cert = cert_map.get(rating, "UN")
                    tn_log(f"[PARENTAL] التقييم النهائي: {cert}")

                    fsk_path = f"/usr/share/enigma2/{self.__path}/FSK_{cert}.png"
                    tn_log(f"[PARENTAL] التحقق من: {fsk_path} → {os.path.exists(fsk_path)}")

                    if os.path.exists(fsk_path):
                        self.instance.setPixmapFromFile(fsk_path)
                        self.instance.show()
                    else:
                        self.instance.hide()
            else:
                self.instance.hide()
                tn_log(f"[PARENTAL] ملف التقييم غير موجود: {rating_file}")

        except Exception as e:
            tn_log(f"[PARENTAL] خطأ: {e}")
            self.instance.hide()