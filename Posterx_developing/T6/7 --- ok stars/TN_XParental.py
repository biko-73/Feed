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

# أنماط البحث عن التقييم في الوصف
PARENTAL_REGEX = [
    r'[+]((\d+))',           # +16
    r'Od lat: ((\d+))',      # Od lat: 18
    r'[Aa]b ((\d+))',        # ab 16
    r'العمر: ((\d+))',       # العمر: 18
    r'عمر: ((\d+))',
]

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nextEvent = 0
        self.clean_name = ""

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "path":
                self.__path = value
            elif attr == "nextEvent":
                self.nextEvent = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        try:
            event = None

            if hasattr(self.source, "event") and self.source.event:
                event = self.source.event
            elif hasattr(self.source, "service"):
                try:
                    ref = self.source.service
                    if ref:
                        from enigma import eEPGCache
                        epg = eEPGCache.getInstance()
                        events = epg.lookupEvent(['T', (ref.toString(), 0, -1, 10)])
                        if events and len(events) > self.nextEvent:
                            title = events[self.nextEvent][0]
                            from enigma import eServiceEvent
                            evt = eServiceEvent()
                            evt.m_event_name = title
                            event = evt
                except Exception:
                    pass

            if not event:
                self.instance.hide()
                return

            title = event.getEventName()
            short = event.getShortDescription()
            full = event.getExtendedDescription()
            desc = short + " " + full

            self.clean_name = re.sub(REGEX_CLEAN, '', title).strip()

            # أولًا: ابحث في الوصف
            parentName = ""
            for pattern in PARENTAL_REGEX:
                match = re.search(pattern, desc)
                if match:
                    parentName = match.group(1).replace("7", "6")  # 7 → 6
                    break

            # ثانيًا: إذا لم يوجد، اقرأ من الملف
            if not parentName:
                rating_file = os.path.join(pathLoc, f"{self.clean_name}.txt")
                if os.path.exists(rating_file):
                    with open(rating_file, "r") as f:
                        rating = f.read().strip()
                        cert_map = {
                            "TV-Y7": "6", "TV-Y": "6", "TV-14": "12", "TV-PG": "16",
                            "TV-G": "0", "TV-MA": "18", "PG-13": "16", "R": "18", "G": "0"
                        }
                        parentName = cert_map.get(rating, "")

            if parentName:
                fsk_path = f"/usr/share/enigma2/RED_DRAGON_FHD/parental/FSK_{parentName}.png"
                if os.path.exists(fsk_path):
                    self.instance.setPixmapFromFile(fsk_path)
                    self.instance.show()
                else:
                    self.instance.hide()
            else:
                self.instance.hide()
        except:
            self.instance.hide()