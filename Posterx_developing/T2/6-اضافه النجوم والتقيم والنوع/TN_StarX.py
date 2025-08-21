# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap, eTimer
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.CurrentService import CurrentService
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Renderer.TNPosterXDownloadThread import FOLDERS, log
from Components.Renderer.TN_lib import get_tmdb_data, search_tmdb
import NavigationInstance
import os

class TN_StarX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.timer = eTimer()
        self.timer.callback.append(self.getStars)
        self.path_folder = FOLDERS["poster"]  # يمكن تغييره حسب الحاجة

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            self.timer.start(100, True)

    def getStars(self):
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
            if not events:
                self.instance.hide()
                return

            event = events[0]
            title = event[4]
            if not title:
                self.instance.hide()
                return

            # --- استخراج السنة ---
            year_match = re.search(r'\b(19|20)\d{2}\b', f"{title} {event[5]} {event[6]}")
            year = year_match.group(0) if year_match else None

            # --- البحث في TMDb ---
            result = search_tmdb(title, year=year)
            if not result:
                self.instance.hide()
                return

            tmdb_id = result["id"]
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(tmdb_id, media_type)
            if not 
                self.instance.hide()
                return

            # --- حساب النجوم (من 0 إلى 5) ---
            rating = data.get("vote_average", 0)  # من 0 إلى 10
            stars = int(round(rating / 2))  # تحويل إلى 0-5
            star_path = f"/usr/share/enigma2/icons/star{stars}.png"  # يجب أن تكون هذه الأيقونات موجودة

            if os.path.exists(star_path):
                self.instance.setPixmapFromFile(star_path)
                self.instance.show()
            else:
                self.instance.hide()

        except Exception as e:
            log(f"[TN_StarX] Error: {e}")
            self.instance.hide()