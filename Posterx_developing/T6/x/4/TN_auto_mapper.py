# -*- coding: utf-8 -*-
# TN_auto_mapper.py - Team Nitro
# سكربت لجمع الأسماء الفاشلة تلقائيًا

import os
import re
import time

LOG_FILE = "/media/hdd/logs/TN_X.log"
OUTPUT_FILE = "/media/hdd/TN_X/failed_titles.txt"

def extract_failed_titles():
    if not os.path.exists(LOG_FILE):
        print("ملف السجل غير موجود:", LOG_FILE)
        return []

    failed = []
    # نمط البحث عن السطر: [FAIL] فشل جميع اللغات لـ: اسم الحدث
    pattern = re.compile(r"\[FAIL\] فشل جميع اللغات لـ: (.+)$")

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            match = pattern.search(line)
            if match:
                title = match.group(1).strip()
                if title and title not in failed:
                    failed.append(title)

    except Exception as e:
        print("خطأ في قراءة السجل:", e)

    return failed

def save_failed_titles(titles):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"# الأسماء الفاشلة - تم الاستخراج في: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# يمكنك مراجعة هذه الأسماء وإضافتها إلى TN_title_mapping.py\n\n")
            for title in sorted(titles):
                f.write(f"{title}\n")
        print(f"تم حفظ {len(titles)} اسمًا فاشلًا في: {OUTPUT_FILE}")
    except Exception as e:
        print("خطأ في حفظ الملف:", e)

if __name__ == "__main__":
    print("جاري استخراج الأسماء الفاشلة...")
    titles = extract_failed_titles()
    if titles:
        save_failed_titles(titles)
    else:
        print("لم يتم العثور على أسماء فاشلة في السجل.")