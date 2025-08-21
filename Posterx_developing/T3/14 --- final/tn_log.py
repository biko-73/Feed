# في بداية الملف
DEBUG = False  # <-- غيرها إلى True فقط عند الحاجة للتصحيح

LOG_FILE = "/media/hdd/logs/TN_PosterX.log"

def tn_log(txt):
    if not DEBUG:
        return
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} - {txt}\n")
    except:
        pass