import os
import time

# Állítsd be a mappa elérési útját
MEDIA_FOLDER = '/home/hypetobuy/htp/media/uploads'

# Törlés minden fájlra, ami régebbi mint 1 óra
now = time.time()
for filename in os.listdir(MEDIA_FOLDER):
    filepath = os.path.join(MEDIA_FOLDER, filename)
    if os.path.isfile(filepath):
        if os.stat(filepath).st_mtime < now - 3600:  # 3600 másodperc = 1 óra
            os.remove(filepath)
