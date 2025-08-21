# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import re
import time

LOG_FILE = "/media/hdd/logs/TN_X.log"

def tn_log(txt):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass

tn_log("=== TN_X تم تحميل الريندر ===")

try:
    from Components.config import config
    lng = config.osd.language.value.split("_")[0]
except:
    lng = "en"
tn_log(f"[CONFIG] اللغة: {lng}")

base_paths = ["/media/hdd", "/media/usb", "/tmp"]
base_folder = "TN_X"
folders = {}

for path in base_paths:
    if os.path.exists(path) and os.access(path, os.W_OK):
        test_path = os.path.join(path, base_folder)
        try:
            for folder in ["poster", "backdrop", "logo", "banner", "rating"]:
                folders[folder] = os.path.join(test_path, folder)
                os.makedirs(folders[folder], exist_ok=True)
            tn_log(f"[PATH] تم استخدام: {test_path}")
            break
        except Exception as e:
            tn_log(f"[PATH] فشل في {path}: {e}")
else:
    fallback = "/tmp/TN_X"
    for folder in ["poster", "backdrop", "logo", "banner", "rating"]:
        folders[folder] = os.path.join(fallback, folder)
        os.makedirs(folders[folder], exist_ok=True)
    tn_log(f"[PATH] استخدام المسار الافتراضي: {fallback}")

REGEX = re.compile(r'[\(\[].*?[\)\]]|:\s*odc\.\s*\d+|S\d+\s*-\s*E\d+|S\d+|E\d+|\s*-\s*S\d+|\s*-\s*Episode\s*\d+|\s*-\s*Part\s*\d+|\s*-\s*ح\s*\d+|\s*-\s*الحلقة\s*\d+|\s*-\s*الجزء\s*\d+|\s*\d+\s*odc|\s*-\s*\d+|\s*\(\w+\)|\s*\[.*?\]|\s*-\s*[^-\s]+$|\s*\(?\d{4}\)?|\s*-\s*-\s*', re.IGNORECASE | re.DOTALL)
def clean_title(title):
    if not title: return ""
    cleaned = re.sub(REGEX, '', title).strip()
    return re.sub(r'\s+', ' ', cleaned)

class TN_X(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.type = "poster"
        self.nextEvent = 0
        self.filename = ""
        self.clean_name = ""
        tn_log("[INIT] TN_X تم تهيئة")

    GUI_WIDGET = ePixmap

    def applySkin(self, desktop, parent):
        for attr, value in self.skinAttributes:
            if attr == "type":
                self.type = value.lower()
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
                tn_log("[SOURCE] تم جلب الحدث من self.source.event")

            elif hasattr(self.source, "service") and self.nextEvent > 0:
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
                        tn_log(f"[EPGCACHE] تم جلب الحدث رقم {self.nextEvent}: {title}")

            if not event:
                tn_log("[EVENT] لا يوجد حدث")
                self.instance.hide()
                return

            title = event.getEventName()
            self.clean_name = clean_title(title)
            if not self.clean_name:
                tn_log("[CLEAN] الاسم فارغ")
                self.instance.hide()
                return

            folder_map = {
                "poster": folders["poster"],
                "backdrop": folders["backdrop"],
                "logo": folders["logo"],
                "banner": folders["banner"]
            }
            ext = ".png" if self.type == "logo" else ".jpg"
            self.filename = os.path.join(folder_map.get(self.type, folders["poster"]), f"{self.clean_name}{ext}")

            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                self.instance.setPixmapFromFile(self.filename)
                self.instance.show()
            else:
                self.instance.hide()
                tn_log(f"[MISSING] الملف غير موجود: {self.filename}")

        except Exception as e:
            tn_log(f"[ERROR] خطأ: {e}")
            self.instance.hide()