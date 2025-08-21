# -*- coding: utf-8 -*-
# TNLogoX.py - عرض الشعار (PNG شفاف)

from Components.Renderer.TNPosterX import TNPosterX

class TNLogoX(TNPosterX):
    def showPoster(self):
        event_name = self.canal[5]
        pstrNm = os.path.join(FOLDERS["logo"], f"{event_name}_logo.png")
        if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
            self.instance.setPixmap(loadJPG(pstrNm))
            self.instance.setScale(1)
            self.instance.show()
        else:
            self.instance.hide()