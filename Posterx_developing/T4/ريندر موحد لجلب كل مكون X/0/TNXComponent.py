# -*- coding: utf-8 -*-
from Components.Converter.Converter import Converter
from Components.Element import cached

class TNXComponent(Converter):
    RATING = 0
    CAST = 1

    def __init__(self, type):
        Converter.__init__(self, type)
        if type == "rating":
            self.type = self.RATING
        elif type == "cast":
            self.type = self.CAST

    @cached
    def getText(self):
        if self.source and hasattr(self.source, "event"):
            event = self.source.event
            if not event:
                return ""
            title = event.getEventName()
            from .TN_X import clean_title
            clean_name = clean_title(title)
            from .TN_X import folders
            folder = folders["rating"] if self.type == self.RATING else folders["cast"]
            path = f"{folder}/{clean_name}.txt"
            try:
                with open(path, "r") as f:
                    return f.read().strip()
            except:
                return "N/A"
        return ""

    text = property(getText)