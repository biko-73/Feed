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

class TN_XStars(VariableValue, Renderer):
    def __init__(self):
        Renderer.__init__(self)
        VariableValue.__init__(self)
        self.nextEvent = 0
        self.clean_name = ""

    GUI_WIDGET = eSlider

    def postWidgetCreate(self, instance):
        instance.setRange(0, 100)

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nextEvent":
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
                self.value = 0
                return

            title = event.getEventName()
            self.clean_name = re.sub(REGEX_CLEAN, '', title).strip()

            score_file = os.path.join(pathLoc, f"{self.clean_name}_score.txt")
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    try:
                        rating = float(f.read().strip())
                        self.value = int(rating * 10)
                    except:
                        self.value = 0
            else:
                self.value = 0

        except Exception as e:
            self.value = 0