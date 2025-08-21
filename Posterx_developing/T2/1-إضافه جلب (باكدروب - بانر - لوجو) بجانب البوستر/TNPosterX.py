# -*- coding: utf-8 -*-
# PosterX - Automatic Poster & Art Renderer for Enigma2
# by digiteng, sunriser, beber
# Modified & Enhanced by Enigma2 Developer (2025)
# دعم: Poster, Backdrop, Banner, Logo من TMDb + Fanart.tv + TheTVDB + Google

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer, loadJPG
from ServiceReference import ServiceReference
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.CurrentService import CurrentService
from Components.Sources.EventInfo import EventInfo
from Components.Sources.Event import Event
from Components.Renderer.TNPosterXDownloadThread import TNPosterXDownloadThread

import NavigationInstance
import os
import sys
import re
import time
import socket
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

# --- تحديد اللغة ---
try:
    from Components.config import config
    lng = config.osd.language.value[:2]  # مثل: en, ar, fr
except:
    lng = "en"

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

# --- تنظيف اسم الفيلم ---
REGEX = re.compile(
    r'([\(\[]).*?([\)\]])|'
    r'(: odc.\d+)|(\d+: odc.\d+)|(\d+ odc.\d+)|(:)|'
    r'( -(.*?).*)|(,)|!|/.*|'
    r'\|\s[0-9]+\+|[0-9]+\+|'
    r'\s\d{4}\Z|'
    r'([\(\[\|].*?[\)\]\|])|'
    r'(\"|\"\.|\"\,|\.)\s.+|'
    r'\"|:|'
    r'Премьера\.\s|'
    r'(х|Х|م|М|ت|ت|د|د)/ф\s|'
    r'(х|Х|م|М|ت|ت|د|د)/س\s|'
    r'\s(س|س)(езон|يريا|-ن|-ي)\s.+|'
    r'\s\d{1,3}\s(س|س\.|د\.|د)\s.+|'
    r'\.\s\d{1,3}\s(س|س\.|د\.|د)\s.+|'
    r'\s(س|س\.|د\.|د)\s\d{1,3}.+|'
    r'\d{1,3}(-ي|-ي|\sس-ن).+|', re.DOTALL)

def convtext(text):
    if not text:
        return ""
    text = REGEX.sub('', text).strip().replace('\xc2\x86', '').replace('\xc2\x87', '')
    try:
        text = str(text, 'utf-8') if not PY3 and isinstance(text, bytes) else text
    except:
        pass
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text.upper().strip()

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
                        dwn_poster = os.path.join(os.path.dirname(threadDB.path_folder), canal[5] + ".jpg")
                        if not os.path.exists(dwn_poster):
                            val, log = self.search_tmdb(dwn_poster, title, evt[6], evt[5], canal[0])
                            if val:
                                newfd += 1
                            elif lng == "fr":
                                val, log = self._fetch_from_google(dwn_poster, title, evt[6], evt[5])
                                if val:
                                    newfd += 1
                except:
                    continue

            # تنظيف الملفات القديمة (> 3 أيام)
            now = time.time()
            for folder in [threadDB.path_folder, threadDB.backdrop_folder, threadDB.banner_folder, threadDB.logo_folder]:
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

            pstrNm = os.path.join(os.path.dirname(threadDB.path_folder), self.canal[5] + ".jpg")
            if os.path.exists(pstrNm):
                self.timer.start(100, True)
            else:
                pdb.put(self.canal[:])
                start_new_thread(self.waitPoster, ())

        except Exception as e:
            print(f"[TNPosterX] Error: {e}")
            self.instance.hide()

    def showPoster(self):
        pstrNm = os.path.join(os.path.dirname(threadDB.path_folder), self.canal[5] + ".jpg")
        if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
            self.instance.setPixmap(loadJPG(pstrNm))
            self.instance.setScale(2)
            self.instance.show()
        else:
            self.instance.hide()

    def waitPoster(self):
        pstrNm = os.path.join(os.path.dirname(threadDB.path_folder), self.canal[5] + ".jpg")
        for _ in range(180):
            if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
                self.timer.start(10, True)
                return
            time.sleep(0.5)
        self.instance.hide()