# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import re

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    base_paths = ["/media/hdd", "/media/usb", "/tmp"]
    for path in base_paths:
        test_path = os.path.join(path, "TN_X", "rating")
        if os.path.exists(test_path):
            pathLoc = test_path
            break
    else:
        pathLoc = "/tmp/TN_X/rating"
    os.makedirs(pathLoc, exist_ok=True)

try:
    from .TN_XTools import clean_title
except:
    REGEX_CLEAN = re.compile(r'[\(\[].*?[\)\]]|:\s*odc\.\s*\d+|S\d+\s*-\s*E\d+|S\d+|E\d+|\s*-\s*S\d+|\s*-\s*Episode\s*\d+|\s*-\s*Part\s*\d+|\s*-\s*ح\s*\d+|\s*-\s*الحلقة\s*\d+|\s*-\s*الجزء\s*\d+|\s*\d+\s*odc|\s*-\s*\d+|\s*\(\w+\)|\s*\[.*?\]|\s*-\s*[^-\s]+$|\s*\(?\d{4}\)?|\s*-\s*-\s*', re.IGNORECASE | re.DOTALL)
    def clean_title(title):
        if not title: return ""
        cleaned = re.sub(REGEX_CLEAN, '', title).strip()
        return re.sub(r'\s+', ' ', cleaned)

# يمكن تمرير اسم السكين من XML لاحقًا
curskin = "RED_DRAGON_FHD"  # افتراضي، يمكن تغييره في XML
pratePath = f"/usr/share/enigma2/{curskin}/parental/"

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
            elif attr == "skin":
                global curskin, pratePath
                curskin = value
                pratePath = f"/usr/share/enigma2/{curskin}/parental/"
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
            self.clean_name = clean_title(title)

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
                    fsk_path = f"{pratePath}FSK_{cert}.png"

                    if os.path.exists(fsk_path):
                        self.instance.setPixmapFromFile(fsk_path)
                        self.instance.show()
                    else:
                        self.instance.hide()
            else:
                self.instance.hide()
        except:
            self.instance.hide()