# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import re
import json

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    pathLoc = "/tmp/TN_X/rating"
    if not os.path.exists(pathLoc):
        os.makedirs(pathLoc)

curskin = "RED_DRAGON_FHD"
pratePath = f"/usr/share/enigma2/{curskin}/parental/"

# تنظيف العناوين
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

# أنماط التقييم في الوصف
PPR = [
    r"\b([aA]b)\s+(\d+)",      # ab 16
    r"\b(\+)(\d+)",            # +18
    r"\b(Od lat:)\s+(\d+)",    # Od lat: 12
    r"\b(العمر:)\s*(\d+)",     # العمر: 16
    r"\b(Age:)\s*(\d+)",       # Age: 18
]

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.clean_name = ""
        tn_log("=== TN_XParental تم تهيئة ===")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "path":
                self.__path = value
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[PARENTAL] تم استدعاء changed: {what}")
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        try:
            event = None
            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
            else:
                tn_log("[PARENTAL] لا يمكن جلب الحدث")
                return

            if not event:
                self.instance.hide()
                return

            title = event.getEventName()
            short = event.getShortDescription()
            full = event.getExtendedDescription()

            # 1. أولًا: جرب استخراج التقييم من الوصف
            fd = f"{title} {short} {full}"
            parentName = ""
            for pattern in PPR:
                match = re.search(pattern, fd, re.IGNORECASE)
                if match:
                    try:
                        parentName = match.group(2)
                        parentName = parentName.replace("7", "6")  # 7 → 6
                        tn_log(f"[PARENTAL] تم استخراج التقييم من الوصف: {parentName}")
                        break
                    except:
                        pass

            # 2. إذا فشل، جرب ملف rating.txt
            if not parentName:
                self.clean_name = re.sub(REGEX_CLEAN, '', title).strip()
                tn_log(f"[PARENTAL] الاسم النظيف: {self.clean_name}")

                rating_file = os.path.join(pathLoc, f"{self.clean_name}.txt")
                if os.path.exists(rating_file):
                    with open(rating_file, "r") as f:
                        rating = f.read().strip()
                        tn_log(f"[PARENTAL] التقييم من TMDB: {rating}")

                        # تحويل التقييم إلى رقم
                        rating_map = {
                            "G": "0", "TV-G": "0", "U": "0",
                            "PG": "16", "TV-PG": "16", "PG-13": "16",
                            "TV-14": "14", "TV-12": "12", "TV-10": "10",
                            "TV-Y7": "6", "TV-Y": "6",
                            "R": "18", "TV-MA": "18", "NR": "18", "15": "15", "12A": "12",
                            "": "UN", "Not Rated": "UN", "Unrated": "UN", "N/A": "UN"
                        }
                        parentName = rating_map.get(rating, "")

            # 3. عرض الصورة
            if parentName:
                fsk_path = f"{pratePath}FSK_{parentName}.png"
                tn_log(f"[PARENTAL] مسار الصورة: {fsk_path}")

                if os.path.exists(fsk_path):
                    self.instance.setPixmapFromFile(fsk_path)
                    self.instance.show()
                else:
                    self.instance.hide()
                    tn_log(f"[PARENTAL] الصورة غير موجودة: {fsk_path}")
            else:
                self.instance.hide()
                tn_log(f"[PARENTAL] لم يتم العثور على تقييم لأي من: {title}")

        except Exception as e:
            tn_log(f"[PARENTAL] خطأ: {e}")
            self.instance.hide()