# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
import os
import time

try:
    from .TN_X import folders
except:
    folders = {
        "poster": "/media/hdd/TN_X/poster",
        "backdrop": "/media/hdd/TN_X/backdrop",
        "logo": "/media/hdd/TN_X/logo",
        "banner": "/media/hdd/TN_X/banner"
    }
    for path in folders.values():
        if not os.path.exists(path):
            os.makedirs(path)

try:
    from .TN_XTools import clean_title
except:
    def clean_title(title):
        return title

class TN_NextEvents(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nextEvent = 0
        self.nxEvntUsed = "poster"
        self.timer = eTimer()
        self.timer.callback.append(self.showPicture)
        self.filename = ""
        self.clean_name = ""

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "nextEvent":
                self.nextEvent = int(value)
            elif attr == "usedImage":
                self.nxEvntUsed = value.lower()
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance:
            return
        if what[0] != self.CHANGED_CLEAR:
            self.instance.hide()
            self.timer.start(100, True)
        else:
            self.instance.hide()

    def showPicture(self):
        try:
            if hasattr(self.source, "service"):
                ref = self.source.service
                if ref:
                    from enigma import eEPGCache
                    epg = eEPGCache.getInstance()
                    events = epg.lookupEvent(['T', (ref.toString(), 0, -1, 10)])
                    if events and len(events) > self.nextEvent:
                        title = events[self.nextEvent][0]
                        self.clean_name = clean_title(title)
                        folder = folders.get(self.nxEvntUsed, folders["poster"])
                        self.filename = os.path.join(folder, f"{self.clean_name}.jpg")

                        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                            self.instance.setPixmapFromFile(self.filename)
                            self.instance.show()
                        else:
                            self.instance.hide()
                    else:
                        self.instance.hide()
                else:
                    self.instance.hide()
            else:
                self.instance.hide()
        except Exception as e:
            self.instance.hide()