# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Components.Renderer.Renderer import Renderer
from Components.VariableValue import VariableValue
from enigma import eSlider
import os
import re

# تعريف tn_log محليًا
LOG_FILE = "/media/hdd/logs/TN_X.log"
def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

import time  # يجب استيراده بعد تعريف tn_log

try:
    from .TN_X import folders
    pathLoc = folders["rating"]
except:
    for path in ["/media/hdd", "/media/usb", "/tmp"]:
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

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.nextEvent = 0
        self.clean_name = ""
        tn_log("=== TN_XStars تم تهيئة ===")

    GUI_WIDGET = eSlider

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nextEvent":
                self.nextEvent = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        tn_log(f"[STARS] تم استدعاء changed: {what}")
        if not self.instance:
            return

        try:
            event = None

            if hasattr(self.source, "service"):
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
                except Exception as e:
                    tn_log(f"[EPGCACHE] خطأ: {e}")

            if not event:
                self.value = 0
                return

            title = event.getEventName()
            self.clean_name = clean_title(title)
            tn_log(f"[STARS] الاسم النظيف: {self.clean_name}")

            score_file = os.path.join(pathLoc, f"{self.clean_name}_score.txt")
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    try:
                        rating = float(f.read().strip())
                        self.value = int(rating * 10)  # 7.5 → 75
                    except:
                        self.value = 0
            else:
                self.value = 0

        except Exception as e:
            tn_log(f"[STARS] خطأ: {e}")
            self.value = 0