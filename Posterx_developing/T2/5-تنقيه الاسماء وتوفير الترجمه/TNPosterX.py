# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from ServiceReference import ServiceReference
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.CurrentService import CurrentService
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Renderer.TNPosterXDownloadThread import FOLDERS, TNPosterXDownloadThread, convtext, log
import NavigationInstance
import os

# --- إنشاء الخيط ---
if not hasattr(TNPosterXDownloadThread, 'instance'):
    TNPosterXDownloadThread.instance = TNPosterXDownloadThread()

threadDB = TNPosterXDownloadThread.instance

class TNPosterX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.nxts = 0
        self.canal = [None] * 6
        self.oldCanal = None
        self.timer = eTimer()
        self.timer.callback.append(self.showPoster)

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attrib, value in self.skinAttributes:
            if attrib == "nexts":
                self.nxts = int(value)
        return Renderer.applySkin(self, desktop, parent)

    def changed(self, what):
        if not self.instance or what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        service = None
        try:
            if isinstance(self.source, Event):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
            elif isinstance(self.source, EventInfo):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
            elif isinstance(self.source, CurrentService):
                service = self.source.getCurrentServiceRef()
            elif isinstance(self.source, ServiceEvent):
                service = self.source.getCurrentService()

            if not service:
                self.instance.hide()
                return

            events = eEPGCache.getInstance().lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
            if len(events) <= self.nxts:
                self.instance.hide()
                return

            event = events[self.nxts]
            title = event[4] or ""
            shortdesc = event[5] or ""
            fulldesc = event[6] or ""

            event_name = convtext(title)
            pstrNm = os.path.join(FOLDERS["poster"], f"{event_name}.jpg")

            self.canal = [
                ServiceReference(service).getServiceName(),
                event[1], title, shortdesc, fulldesc, event_name
            ]

            curCanal = f"{event[1]}-{event_name}"
            if curCanal == self.oldCanal:
                return
            self.oldCanal = curCanal

            if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
                self.instance.setPixmap(loadJPG(pstrNm))
                self.instance.setScale(2)
                self.instance.show()
            else:
                threadDB.queue.put(self.canal[:])
                self.wait_and_show(pstrNm)

        except Exception as e:
            log(f"[TNPosterX] Error in changed(): {e}")
            self.instance.hide()

    def wait_and_show(self, pstrNm):
        for _ in range(180):
            if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
                self.timer.start(10, True)
                return
            time.sleep(0.5)
        self.instance.hide()

    def showPoster(self):
        try:
            self.changed((self.CHANGED_DEFAULT,))
        except Exception as e:
            log(f"[TNPosterX] Error in showPoster: {e}")