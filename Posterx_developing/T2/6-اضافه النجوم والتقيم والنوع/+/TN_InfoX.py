# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import eLabel
from Components.Sources.Event import Event
from Components.Renderer.TN_lib import get_tmdb_data, search_tmdb
import NavigationInstance

class TN_InfoX(Renderer):
    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        if self.instance:
            self.getFullInfo()

    def getFullInfo(self):
        try:
            # --- الحصول على الخدمة والحدث ---
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

            # --- البحث في TMDb ---
            result = search_tmdb(title)
            if not result:
                self.instance.setText("معلومات غير متوفرة")
                return

            tmdb_id = result["id"]
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(tmdb_id, media_type)
            if not 
                self.instance.setText("")
                return

            # --- جمع المعلومات ---
            info_parts = []

            # 1. النوع
            genres = [g["name"] for g in data.get("genres", [])]
            if genres:
                info_parts.append(" | ".join(genres[:3]))  # أول 3 أنواع

            # 2. السنة
            if media_type == "movie":
                year = data.get("release_date", "")[:4]
            else:
                year = data.get("first_air_date", "")[:4]
            if year:
                info_parts.append(year)

            # 3. المدة
            if media_type == "movie":
                runtime = data.get("runtime")
            else:
                runtime = data.get("episode_run_time", [None])[0]
            if runtime:
                info_parts.append(f"{runtime} دقيقة")

            # 4. التقييم
            rating = data.get("vote_average", 0)
            if rating > 0:
                info_parts.append(f"تقييم: {rating}/10")

            # 5. التصنيف العمري
            parental = self.get_parental(data.get("content_ratings", {}))
            if parental != "+غير معروف":
                info_parts.append(parental)

            # --- دمج المعلومات ---
            full_text = " • ".join(info_parts)
            self.instance.setText(full_text if full_text else "معلومات غير متوفرة")

        except Exception as e:
            log(f"[TN_InfoX] Error: {e}")
            self.instance.setText("خطأ في التحميل")

    def get_parental(self, content_ratings):
        for r in content_ratings.get("results", []):
            if r.get("iso_3166_1") == "US":
                code = r.get("rating", "")
                return {"G": "+جميع", "PG": "+7", "PG-13": "+13", "R": "+16", "NC-17": "+18"}.get(code, code)
        return "+غير معروف"