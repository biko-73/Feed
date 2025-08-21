# -*- coding: utf-8 -*-
# TNbannerX.py - عرض البنر

from Components.Renderer.TNPosterX import TNPosterX

class TNbannerX(TNPosterX):
    def showPoster(self):
        event_name = self.canal[5]
        pstrNm = os.path.join(FOLDERS["banner"], f"{event_name}_banner.jpg")
        if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
            self.instance.setPixmap(loadJPG(pstrNm))
            self.instance.setScale(1)
            self.instance.show()
        else:
            self.instance.hide()