# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import eLabel
from Components.Sources.Event import Event
from Components.Sources.EventInfo import EventInfo
from Components.Sources.CurrentService import CurrentService
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Renderer.TN_lib import get_tmdb_data, search_tmdb
import NavigationInstance

# --- خرائط التصنيف ---
MPAA_TO_AR = {
    "G": "+جميع الأعمار",
    "PG": "+7",
    "PG-13": "+13",
    "R": "+16",
    "NC-17": "+18"
}

def get_parental_rating(content_ratings, iso="US"):
    for rating in content_ratings.get("results", []):
        if rating.get("iso_3166_1") == iso:
            code = rating.get("rating", "")
            return MPAA_TO_AR.get(code, code)
    return "+غير معروف"

class TN_ParentalX(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        self.text = ""

    GUI_WIDGET = eLabel

    def changed(self, what):
        if self.instance:
            self.getParental()

    def getParental(self):
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

            year_match = re.search(r'\b(19|20)\d{2}\b', f"{title} {event[5]} {event[6]}")
            year = year_match.group(0) if year_match else None

            result = search_tmdb(title, year=year)
            if not result:
                self.instance.setText("")
                return

            tmdb_id = result["id"]
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(tmdb_id, media_type)
            if not 
                self.instance.setText("")
                return

            rating = get_parental_rating(data.get("content_ratings", {}), "US")
            self.instance.setText(rating)

        except Exception as e:
            log(f"[TN_ParentalX] Error: {e}")
            self.instance.setText("")