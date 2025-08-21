# -*- coding: utf-8 -*-
# PosterX - Automatic Poster & Art Renderer for Enigma2
# by digiteng, sunriser, beber
# Modified & Enhanced by Enigma2 Developer (2025)
# دعم: Poster, Backdrop, Banner, Logo من TMDb + Fanart.tv + TheTVDB + Google
# مع إدارة تلقائية للذاكرة

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from ServiceReference import ServiceReference
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.Sources.EventInfo import EventInfo
from Components.Sources.Event import Event
from Components.Renderer.TNPosterXDownloadThread import FOLDERS, TNPosterXDownloadThread, convtext

import NavigationInstance
import os
import sys
import re
import time
import unicodedata

PY3 = sys.version_info[0] == 3

try:
    if PY3:
        import queue
        from _thread import start_new_thread
    else:
        import Queue
        from thread import start_new_thread
except:
    pass

epgcache = eEPGCache.getInstance()

# --- قاعدة بيانات القنوات التلقائية ---
apdb = {}
autobouquet_file = '/etc/enigma2/userbouquet.favourites.tv'
autobouquet_count = 32

if os.path.exists(autobouquet_file):
    try:
        with open(autobouquet_file, 'r') as f:
            lines = f.readlines()
        for i in range(min(autobouquet_count, len(lines))):
            if '#SERVICE' in lines[i]:
                line = lines[i][9:].strip().split(':')
                if len(line) == 11:
                    value = ':'.join((line[3], line[4], line[5], line[6]))
                    if value != '0:0:0:0':
                        service = ':'.join(line[:11])
                        apdb[i] = service
    except:
        pass

# --- صف الانتظار ---
if PY3:
    pdb = queue.LifoQueue()
else:
    pdb = Queue.LifoQueue()

# --- خيط التنزيل ---
threadDB = TNPosterXDownloadThread()
threadDB.start()

# --- خيط البحث التلقائي ---
class AutoDB(TNPosterXDownloadThread):
    def __init__(self):
        TNPosterXDownloadThread.__init__(self)

    def run(self):
        while True:
            time.sleep(7200)  # كل ساعتين
            newfd = 0
            for service in apdb.values():
                try:
                    events = epgcache.lookupEvent(['IBDCTESX', (service, 0, -1, 1440)])
                    for evt in events:
                        title = evt[4]
                        if not title:
                            continue
                        canal = [
                            ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', ''),
                            evt[1], title, evt[5], evt[6], convtext(title)
                        ]
                        dwn_poster = os.path.join(FOLDERS["poster"], canal[5] + ".jpg")
                        if not os.path.exists(dwn_poster):
                            val, log = self.search_tmdb(dwn_poster, title, evt[6], evt[5], canal[0])
                            if val:
                                newfd += 1
                            elif self._fetch_from_google(dwn_poster, title, evt[6], evt[5]):
                                newfd += 1
                except:
                    continue

            # تنظيف الملفات القديمة (> 3 أيام)
            now = time.time()
            for folder in FOLDERS.values():
                for f in os.listdir(folder):
                    fp = os.path.join(folder, f)
                    if os.path.isfile(fp) and (now - os.path.getmtime(fp)) > 259200:
                        os.remove(fp)

threadAutoDB = AutoDB()
threadAutoDB.start()

# --- الرياندر الرئيسي ---
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
        if not self.instance:
            return
        if what[0] == self.CHANGED_CLEAR:
            self.instance.hide()
            return

        servicetype = None
        service = None
        try:
            if isinstance(self.source, ServiceEvent):
                service = self.source.getCurrentService()
                servicetype = "ServiceEvent"
            elif isinstance(self.source, CurrentService):
                service = self.source.getCurrentServiceRef()
                servicetype = "CurrentService"
            elif isinstance(self.source, EventInfo):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                servicetype = "EventInfo"
            elif isinstance(self.source, Event):
                if self.nxts:
                    service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
                else:
                    self.canal[0] = None
                    self.canal[1] = self.source.event.getBeginTime()
                    self.canal[2] = self.source.event.getEventName() or ""
                    self.canal[3] = self.source.event.getExtendedDescription() or ""
                    self.canal[4] = self.source.event.getShortDescription() or ""
                    self.canal[5] = convtext(self.canal[2])
                servicetype = "Event"

            if service:
                events = epgcache.lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
                if len(events) > self.nxts:
                    self.canal[0] = ServiceReference(service).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    self.canal[1] = events[self.nxts][1]
                    self.canal[2] = events[self.nxts][4] or ""
                    self.canal[3] = events[self.nxts][5] or ""
                    self.canal[4] = events[self.nxts][6] or ""
                    self.canal[5] = convtext(self.canal[2])
                    if self.canal[0] not in apdb:
                        apdb[self.canal[0]] = service.toString()

            if not servicetype:
                self.instance.hide()
                return

            curCanal = "{}-{}".format(self.canal[1], self.canal[2])
            if curCanal == self.oldCanal:
                return
            self.oldCanal = curCanal

            pstrNm = os.path.join(FOLDERS["poster"], self.canal[5] + ".jpg")
            if os.path.exists(pstrNm):
                self.timer.start(100, True)
            else:
                pdb.put(self.canal[:])
                start_new_thread(self.waitPoster, ())

        except Exception as e:
            print(f"[TNPosterX] Error: {e}")
            self.instance.hide()

    def showPoster(self):
        pstrNm = os.path.join(FOLDERS["poster"], self.canal[5] + ".jpg")
        if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
            self.instance.setPixmap(loadJPG(pstrNm))
            self.instance.setScale(2)
            self.instance.show()
        else:
            self.instance.hide()

    def waitPoster(self):
        pstrNm = os.path.join(FOLDERS["poster"], self.canal[5] + ".jpg")
        for _ in range(180):
            if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
                self.timer.start(10, True)
                return
            time.sleep(0.5)
        self.instance.hide()