# -*- coding: utf-8 -*-
from Components.Renderer.Renderer import Renderer
from enigma import eLabel
from Components.Sources.Event import Event
from Components.Renderer.TN_lib import get_tmdb_data, search_tmdb
import NavigationInstance

class TN_YearX(Renderer):
    def __init__(self):
        Renderer.__init__(self)

    GUI_WIDGET = eLabel

    def changed(self, what):
        if self.instance:
            self.getYear()

    def getYear(self):
        try:
            # ... (كما في السابق: الحصول على service و event)

            result = search_tmdb(title)
            if not result:
                self.instance.setText("")
                return

            tmdb_id = result["id"]
            media_type = "movie" if result.get("title") else "tv"
            data = get_tmdb_data(tmdb_id, media_type)
            if not 
                self.instance.setText("")
                return

            # --- استخراج السنة ---
            if media_type == "movie":
                release_date = data.get("release_date", "")
                year = release_date[:4] if release_date else "غير معروف"
                self.instance.setText(year)
            else:
                first = data.get("first_air_date", "")[:4]
                last = data.get("last_air_date", "")[:4]
                if first and last:
                    self.instance.setText(f"{first} - {last}")
                elif first:
                    self.instance.setText(first)
                else:
                    self.instance.setText("غير معروف")

        except Exception as e:
            log(f"[TN_YearX] Error: {e}")
            self.instance.setText("")