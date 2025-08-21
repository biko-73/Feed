# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
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

class TN_XParental(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nextEvent = 0
        self.path = "/usr/share/enigma2/RED_DRAGON_FHD/parental/"
        self.timer = eTimer()
        self.timer.callback.append(self.showParental)
        self.clean_name = ""

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "path":
                self.path = value
            elif attr == "nextEvent":
                self.nextEvent = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
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
            self.clean_name = re.sub(REGEX_CLEAN, '', title).strip()

            rating_file = os.path.join(pathLoc, f"{self.clean_name}.txt")
            if os.path.exists(rating_file):
                with open(rating_file, "r") as f:
                    rating = f.read().strip()

                    cert_map = {
                        "G": "0", "TV-G": "0", "U": "0",
                        "PG": "16", "TV-PG": "16", "PG-13": "16",
                        "TV-14": "14", "TV-12": "12", "TV-10": "10",
                        "TV-Y7": "6", "TV-Y": "6",
                        "R": "18", "TV-MA": "18", "NR": "18", "15": "15", "12A": "12",
                        "": "UN", "Not Rated": "UN", "Unrated": "UN", "N/A": "UN"
                    }
                    cert = cert_map.get(rating, "UN")
                    self.fsk_path = os.path.join(self.path, f"FSK_{cert}.png")

                    # اعرض الصورة فورًا إذا كانت موجودة
                    if os.path.exists(self.fsk_path):
                        self.instance.setPixmapFromFile(self.fsk_path)
                        self.instance.show()
                    else:
                        self.instance.hide()
            else:
                self.instance.hide()
        except:
            self.instance.hide()

    def showParental(self):
        try:
            if self.instance and hasattr(self, "fsk_path") and os.path.exists(self.fsk_path):
                self.instance.setPixmapFromFile(self.fsk_path)
                self.instance.show()
            else:
                self.instance.hide()
        except:
            self.instance.hide()