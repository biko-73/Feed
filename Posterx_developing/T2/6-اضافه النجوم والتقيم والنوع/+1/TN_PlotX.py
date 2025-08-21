# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import eLabel
from Components.Sources.Event import Event
from Components.Renderer.TN_lib import get_tmdb_data, search_tmdb
import NavigationInstance

class TN_PlotX(Renderer):
    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        if self.instance:
            self.getPlot()

    def getPlot(self):
        try:
            service = None
            if isinstance(self.source, Event):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
            elif isinstance(self.source, EventInfo):
                service = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
            elif isinstance(self.source, CurrentService):
                service = self.source.getCurrentServiceRef()
            elif isinstance(self.source, ServiceEvent):
                service = self.source.getCurrentService()

            if not service:
                self.instance.setText("")
                return

            events = eEPGCache.getInstance().lookupEvent(['IBDCTESX', (service.toString(), 0, -1, -1)])
            if not events:
                self.instance.setText("")
                return

            event = events[0]
            title = event[4]
            if not title:
                self.instance.setText("")
                return

            result = search_tmdb(title)
            if not result:
                self.instance.setText("لا يوجد وصف")
                return

            tmdb_id = result["id"]
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(tmdb_id, media_type)
            if not 
                self.instance.setText("")
                return

            overview = data.get("overview", "لا يوجد وصف متاح")
            # تقليل الطول إذا كان طويلًا
            if len(overview) > 200:
                overview = overview[:197] + "..."

            self.instance.setText(overview)

        except Exception as e:
            log(f"[TN_PlotX] Error: {e}")
            self.instance.setText("خطأ في التحميل")