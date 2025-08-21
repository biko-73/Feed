# -*- coding: utf-8 -*-
# TNBackdropX.py - عرض الخلفية

from Components.Renderer.TNPosterX import TNPosterX

class TNBackdropX(TNPosterX):
    def showPoster(self):
        event_name = self.canal[5]
        pstrNm = os.path.join(FOLDERS["backdrop"], f"{event_name}_backdrop.jpg")
        if os.path.exists(pstrNm) and os.path.getsize(pstrNm) > 0:
            self.instance.setPixmap(loadJPG(pstrNm))
            self.instance.setScale(1)
            self.instance.show()
        else:
            self.instance.hide()