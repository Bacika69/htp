


from django.shortcuts import render
from .models import Shoe, Márka, bestseller
from bs4 import BeautifulSoup
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import os
import random
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q
from concurrent.futures import ThreadPoolExecutor
import time
from selenium.webdriver.support.ui import Select



from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cv2
import os
import math

def home(request):
    image_url = None
    szo = ""
    szam = ""
    mondat = ""
    mondat2 = ""
    mondat3 = ""
    error = ""

    # Referencia képek
    img_tabs = [
        ["tab1_img1.jpg", "tab1_img2.jpg", "tab1_img3.jpg"],
        ["tab2_img1.jpg", "tab2_img2.jpg", "tab2_img3.jpg"],
        ["tab3_img1.jpg", "tab3_img2.jpg", "tab3_img3.jpg"],
        ["tab4_img1.jpg", "tab4_img2.jpg", "tab4_img3.jpg"],
        ["tab5_img1.jpg", "tab5_img2.jpg", "tab5_img3.jpg"],
        ["tab6_img1.jpg", "tab6_img2.jpg", "tab6_img3.jpg"],
        ["tab7_img1.jpg", "tab7_img2.jpg", "tab7_img3.jpg"]
    ]

    értékek = {
        1: ("Sub-5", "2", "Bad eye area", "Bad skin", "Bad jawline and chin"),
        2: ("Sub-3", "15", "Bad eye area", "Normal skin", "Bad jawline and chin"),
        3: ("LTN", "25", "Normal eye area", "Normal skin", "Bad jawline and chin"),
        4: ("MTN", "45", "Normal eye area", "Normal skin", "Normal jawline and chin"),
        5: ("HTN", "75", "Good eye area", "Normal skin", "Nice jawline and chin"),
        6: ("Chadlite", "90", "Good eye area", "Nice skin", "Sharp jawline and chin"),
        7: ("Chad", "99", "Perfect eye area", "Perfect skin", "Perfect jawline and chin")
    }

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        try:
            # Kép mentése
            filename = default_storage.save('uploads/' + image.name, ContentFile(image.read()))
            image_url = '/media/' + filename

            # Arcérzékelő inicializálása
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Feltöltött kép feldolgozása
            img_path = default_storage.path(filename)
            img1 = cv2.imread(img_path)
            if img1 is None:
                error = "A kép betöltése sikertelen"
            else:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                
                # Arc detektálása a feltöltött képen
                faces1 = face_cascade.detectMultiScale(gray1, 1.1, 4)
                if len(faces1) == 0:
                    error = "Nem található arc a képen"
                else:
                    # Csak a legnagyobb arcot használjuk
                    x, y, w, h = max(faces1, key=lambda face: face[2] * face[3])
                    face_roi1 = gray1[y:y+h, x:x+w]
                    face_roi1 = cv2.resize(face_roi1, (200, 200))  # Standard méret

                    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    STATIC_IMG_DIR = os.path.join(BASE_DIR, 'static', 'images')

                    best_sim = -1
                    best_tab = -1

                    for tab_idx, tab_imgs in enumerate(img_tabs, 1):
                        for img_name in tab_imgs:
                            ref_path = os.path.join(STATIC_IMG_DIR, img_name)
                            if not os.path.exists(ref_path):
                                continue
                                
                            # Referencia kép feldolgozása
                            img2 = cv2.imread(ref_path)
                            if img2 is None:
                                continue
                                
                            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                            
                            # Arc detektálása a referencia képen
                            faces2 = face_cascade.detectMultiScale(gray2, 1.1, 4)
                            if len(faces2) == 0:
                                continue
                                
                            # Csak a legnagyobb arcot használjuk
                            x2, y2, w2, h2 = max(faces2, key=lambda face: face[2] * face[3])
                            face_roi2 = gray2[y2:y2+h2, x2:x2+w2]
                            face_roi2 = cv2.resize(face_roi2, (200, 200))

                            # Hasonlóság számítása numpy nélkül
                            similarity = calculate_similarity_simple(face_roi1, face_roi2)
                            
                            if similarity > best_sim:
                                best_sim = similarity
                                best_tab = tab_idx

                    # Eredmény hozzárendelése
                    if best_tab in értékek and best_sim > 0.4:  # Minimum hasonlósági küszöb
                        szo, szam, mondat, mondat2, mondat3 = értékek[best_tab]
                    else:
                        error = "Nem található elég hasonló arc a referenciák között"

        except Exception as e:
            error = f"Hiba történt: {str(e)}"

    context = {
        "image_url": image_url,
        "szo": szo,
        "szam": szam,
        "mondat": mondat,
        "mondat2": mondat2,
        "mondat3": mondat3,
        "error": error
    }
    return render(request, 'home.html', context)

def calculate_similarity_simple(img1, img2):
    """
    Egyszerű hasonlóság számítás numpy nélkül
    """
    if img1.shape != img2.shape:
        return 0
    
    total_pixels = img1.shape[0] * img1.shape[1]
    diff_sum = 0
    
    # Képpontonkénti különbség számítása
    for i in range(img1.shape[0]):
        for j in range(img1.shape[1]):
            diff = abs(int(img1[i, j]) - int(img2[i, j]))
            diff_sum += diff
    
    # Átlagos különbség (0-255 skálán)
    avg_diff = diff_sum / total_pixels
    
    # Hasonlóság: 1 - (átlagos különbség / 255)
    similarity = 1 - (avg_diff / 255)
    
    return max(0, min(1, similarity))  # 0 és 1 közé korlátozás

def calculate_similarity_histogram(img1, img2):
    """
    Alternatív megoldás: histogram alapú hasonlóság (gyorsabb)
    """
    # Hisztogram számítása
    hist1 = [0] * 256
    hist2 = [0] * 256
    
    for i in range(img1.shape[0]):
        for j in range(img1.shape[1]):
            hist1[img1[i, j]] += 1
            hist2[img2[i, j]] += 1
    
    # Hisztogram összehasonlítása (Bhattacharyya távolság)
    sum1 = sum2 = sum_product = 0
    for i in range(256):
        sum1 += hist1[i]
        sum2 += hist2[i]
        sum_product += math.sqrt(hist1[i] * hist2[i])
    
    if sum1 == 0 or sum2 == 0:
        return 0
    
    # Bhattacharyya együttható
    bc = sum_product / math.sqrt(sum1 * sum2)
    return bc

def calculate_similarity_orb(img1, img2):
    """
    ORB alapú hasonlóság számítás (a legjobb választás)
    """
    # ORB detektor inicializálása
    orb = cv2.ORB_create()
    
    # Kulcspontok és deskriptorok keresése
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    if des1 is None or des2 is None:
        return 0
    
    # Brute Force Matcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    
    # Hasonlóság számítása
    if len(kp1) == 0 or len(kp2) == 0:
        return 0
    
    similarity = len(matches) / min(len(kp1), len(kp2))
    return similarity























# ...a

def room(request, pk):
    
    shoe = Shoe.objects.get(id=pk) 
    meret = request.GET.get("meret")
    
    shoe.kiv_ár = shoe.méret_ár.get(meret, None)
    shoe.kiv_akcios_ár = shoe.méret_akciosok.get(meret, None)
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'shoe': shoe, 'best_shoes':best_shoes, 'meret': meret}

    return render(request, 'room.html', context)

def sneakerek(request): 
        shoes = Shoe.objects.all()
        if request.GET.get("q") is None or request.GET.get("q") == "":
            cipők = request.session.get('cipők', [])
            
            if cipők:
                shoes = Shoe.objects.filter(id__in=[cipő['id'] for cipő in cipők])
        # shoes = shoes.exclude(name__icontains="(TD & PS)")
        # shoes = shoes.exclude(name__icontains="(Infants)")
        # shoes = shoes.exclude(name__icontains="(TD)")
        
        best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
        
        def seeded_random_sort(shoes, seed_value):
            random.seed(seed_value)  # Fixáljuk a seed-et, hogy mindig ugyanazt az eredményt kapjuk
            shoes = list(shoes)  # Győződj meg róla, hogy lista típusú a shoes
            random.shuffle(shoes)
            return shoes

        query = request.GET.get('q', '') 
    
        rendezes = request.GET.get('r', '')
        if query == 'SALE':
            shoes = shoes.filter(akcios_ár__gt=0)
            shoes = shoes.order_by("-akcios_rendezes")
            shoes = list(shoes)
            

        elif query == 'POPULAR':
            shoes = list(shoes)
            
            rend_cipő = []
            szam = 0
            for cipő in shoes:
                if '00s grey white' in cipő.name.lower() or '00s core black' in cipő.name.lower() or 'low 07 triple white' in cipő.name.lower() or 'military black' in cipő.name.lower() or 'thunder' in cipő.name.lower() or 'mid panda' in cipő.name.lower()  or 'tazz slipper chestnut' in cipő.name.lower():
                    rend_cipő.append(cipő)
                    szam = szam + 1
       
            
            rend_cipő.sort(key=lambda x: int(x.rendszerezes), reverse=True)
            
            def seeded_random_sort(rend_cipő, seed_value):
                random.seed(seed_value)  
                shoes = list(rend_cipő)  
                random.shuffle(rend_cipő)
                return rend_cipő
            shoes = seeded_random_sort(rend_cipő, 0)
            
            
            
            
            
        else:
         
            found_in_best_shoes = False
            if "Air Jordan" in query:
                 query = query.replace("Air Jordan", "Jordan" )
            # Ellenőrizd, hogy a query egy egész márka vagy cipő neve-e
            for brand, models in best_shoes.items():
                if query == brand or query in models:
                    found_in_best_shoes = True
                    # Ha a query egy márka vagy egy konkrét cipőnév, akkor egészében szűrjük
                    shoes = shoes.filter(name__icontains=query)
                    break

            if not found_in_best_shoes:
                # Ha nem találtunk egyezést a best_shoes-ban, akkor szavanként szűrjük
                search_filter = Q()
                for term in query.lower().split():
                    search_filter &= Q(name__icontains=term)
                shoes = shoes.filter(search_filter)
                
            
            
            seed_value = hash(query)  # A keresési lekérdezés hash-e seed-ként
            shoes = seeded_random_sort(shoes, seed_value)
            
            # print(shoes)
            # ak_2 = shoes[1::2]
            # ak_tobbi = shoes[0::2]
            # shoes = ak_2 + ak_tobbi
        from_price = request.GET.get('fromprice')  
        to_price = request.GET.get('toprice')
        if from_price is None and to_price is None or from_price == "" and to_price == "":
           
            pass
        else:
            
            # Ha valamelyik ár intervallum adott, konvertáljuk őket int típusra
            if from_price is not None:
                from_price = int(from_price)
            else:
                from_price = 0  # Alapértelmezett alsó érték, ha nincs megadva

            if to_price is not None:
                to_price = int(to_price)
            else:
                to_price = float('inf')  # Alapértelmezett felső érték, ha nincs megadva

           
            
            # List comprehension-nel szűrjük a termékeket
            meret = request.GET.get("meret")
            
            for cipő in shoes:
                if meret == "None" or meret is None:
                    
                    cipő.kiv_ár = cipő.price
                    
                    cipő.kiv_akcios_ár = cipő.akcios_ár
                else:
                    
                    cipő.kiv_ár = cipő.méret_ár.get(meret, "0")
                    
                    cipő.kiv_akcios_ár = cipő.méret_akciosok.get(meret, "0")
            shoes = [shoe for shoe in shoes if from_price <= int(shoe.kiv_ár.replace(" ", "")) <= to_price]
        meretek = set()
        
        for i in shoes:
             for x in i.méretek:
                  meretek.add(x)
        meretek = sorted(meretek)
        
        
        szinek_alpha = ['White', 'Black', 'Grey', 'Brown', 'Red', 'Orange', 'Blue', 'Green', 'Pink', 'Yellow']
        szinek1 = set()
        
        for x in shoes:
             for y in szinek_alpha:
                  if y in x.name:
                       szinek1.add(y)
        markak_alpha = ['Nike', 'Jordan', 'Adidas', 'Yezzy', 'UGG', 'New Balance', 'Supreme', 'Louis Vuitton', 'Crocs', 'Gucci', 'Puma']
        markak1 = set()
        for x in shoes:
             for y in markak_alpha:
                  if y in x.name:
                       markak1.add(y)
        dbszinek = len(szinek1)

        for h in range(1, dbszinek):
             szin = request.GET.get(f"szin{h}")
             szinek1.discard(szin)
        szinszamok = {}
        
        
        for f in range(1, dbszinek ):
            szinszamok[f + 1] = request.GET.get(f"szin{f}")
        
        szinek_x = {f"{request.GET.get(f'szin{i}')}": "" for i in range(1 ,dbszinek)}
        

        for x in range(1, dbszinek ):
            l = []
            
            for i in range(1, dbszinek ):
                if i == x:
                    # Set `szin{x}` to None
                    l.append(f"szin{i}=None")
                else:
                    # Fetch the value of `szin{i}` from the request, defaulting to an empty string if not present
                    l.append(f"szin{i}={request.GET.get(f'szin{i}', '')}")
            
            # Join the list `l` into a query string prefixed with '&'
            query_string = '&' + '&'.join(l)
            
            # Append the query_string to the appropriate list in the dictionary
            szinek_x[f"{request.GET.get(f'szin{x}')}"] = query_string
     
        j = []
        for x in range(1, dbszinek ):
            
            j.append(f"szin{x}={request.GET.get(f'szin{x}', '')}")
            
        szin_url = '&' + '&'.join(j)
       
        
        markaszamok = {}
        dbmarkak = len(markak1)
        
        for f in range(1, dbmarkak ):
            markaszamok[f + 1] = request.GET.get(f"marka{f}")
        
        # nemtom = "fazs"
        markak_x = {f"{request.GET.get(f'marka{i}')}": "" for i in range(1, dbmarkak)}
        

        for x in range(1, dbmarkak ):
            l = []
            
            for i in range(1, dbmarkak ):
                if i == x:
                    
                    l.append(f"marka{i}=None")
                else:
                    
                    l.append(f"marka{i}={request.GET.get(f'marka{i}', '')}")
            
            
            query_string = '&' + '&'.join(l)
            
            
            markak_x[f"{request.GET.get(f'marka{x}')}"] = query_string
        é = []
        for x in range(1, dbmarkak ):
            
            é.append(f"marka{x}={request.GET.get(f'marka{x}', '')}")
            
        marka_url = '&' + '&'.join(é)
        filtered_shoes = []


        markak_lista = []
        for x in range(1, dbmarkak):
            markak_lista.append(request.GET.get(f"marka{x}"))
        markak_lista = [marka for marka in markak_lista if marka != "" and marka != ""  "None" and marka is not None]  # Üres értékek kiszűrése

        # Gyűjtsük össze a színeket a szűréshez
        colors = []
        for x in range(1, dbszinek):
            colors.append(request.GET.get(f"szin{x}"))
        colors = [color for color in colors if color != "" and color != ""  "None"  and color is not None]  # Üres értékek kiszűrése

        # szinek es markak kivalasztasa
        meret = request.GET.get("meret")
        # csakmeretszures = [] 
        # if meret == None:
        #     csakmeretszures = shoes
        # else:
        #     for a in shoes:
        #             if meret in a.méretek:
        #                 csakmeretszures.append(a)
        
        # csakszinszures = []
        # if colors != []:
        #     for a in shoes:
        #         for b in colors:
        #             if b.lower() in a.name.lower():
        #                 csakszinszures.append(a)
        # else:
        #      csakszinszures = shoes
        # csakmarkaszures = []
        # if markak_lista != []:
        #     for a in shoes:
        #         for b in markak_lista:
        #             if b.lower() in a.name.lower():
        #                 csakmarkaszures.append(a)
        # else:
        #      csakmarkaszures = shoes
        # szinek = set()

        # for x in csakmarkaszures:
        #      for y in szinek_alpha:
        #           if y.lower() in x.name.lower():
        #                szinek.add(y)
        # for h in range(1, dbszinek):
        #      szin = request.GET.get(f"szin{h}")
        #      szinek.discard(szin)
        # markak = set()
        # for x in csakszinszures:
        #      for y in markak_alpha:
        #           if y in x.name:
        #                markak.add(y)
        # for h in range(1, dbmarkak):
        #      marka = request.GET.get(f"marka{h}")
        #      markak.discard(marka)
        
        
        for shoe in shoes:
            # Méretszűrés
            if meret != "None":
                size_match = not meret or meret in shoe.méretek  # Ha nincs méret megadva, minden cipő elfogadható
            
                # Színszűrés
                color_match = not colors or any(color.lower() in shoe.name.lower() for color in colors)
                
                # Márkaszűrés
                marka_match = not markak_lista or any(marka.lower() in shoe.name.lower() for marka in markak_lista)
                
                # Csak akkor adjuk hozzá, ha az összes feltétel teljesül
                if size_match and color_match and marka_match:
                    filtered_shoes.append(shoe)
            else:
                 # Színszűrés
                color_match = not colors or any(color.lower() in shoe.name.lower() for color in colors)
                
                # Márkaszűrés
                marka_match = not markak_lista or any(marka.lower() in shoe.name.lower() for marka in markak_lista)
                
                # Csak akkor adjuk hozzá, ha az összes feltétel teljesül
                if color_match and marka_match:
                    filtered_shoes.append(shoe)

        
        

        if filtered_shoes:
            
            
            
            if query != 'SALE':
                shoes = list(set(filtered_shoes))
                shoes.sort(key=lambda x: int(x.rendszerezes), reverse=True)
                shoes = seeded_random_sort(shoes, 980)
        
        
        
        
        
        
        osszes_x_lehet = "nem"
        osszes_x_szam = 0

        for x in markak_lista:
            
            if x in markak_alpha:
                
                osszes_x_szam += 1
        for xx in colors:
             
             if xx in szinek_alpha:
                
                  osszes_x_szam += 1
        
        
        if osszes_x_szam > 1:
             osszes_x_lehet = "igen"
        
        
        # if query == "SALE" and from_price is None and to_price is None or from_price == "" and to_price == "" and query == "SALE":
        #     if rendezes == "Legalacsonyabb ár":
        #         shoes = shoes.order_by('rendszerezes')
        #     elif rendezes == "Legmagasabb ár":
        #         shoes = shoes.order_by('-rendszerezes')
        #     elif rendezes in szinek:
                
        #         if rendezes == "White":
        #             shoes = shoes.filter(name__icontains=" White")
                    
        #         else:
        #             shoes = shoes.filter(name__icontains=rendezes)
        #     elif rendezes == "Leárazás":
        #         shoes = shoes.filter(akcios_ár__gt=0)
        #     else:
        #         shoes = list(shoes)
            
        # else:
        try:
            tesztshoe = [shoe for shoe in shoes if shoe.akcios_ár != "0"]
             
            if not tesztshoe:
                  rendezes_allow = "nem"
            else:
                rendezes_allow = "igen"
        except:
             rendezes_allow = "igen"
             pass
        
        if rendezes == "Legalacsonyabb ár":
                shoes.sort(key=lambda x: int(x.rendszerezes), reverse=False)
        elif rendezes == "Legmagasabb ár":
                shoes.sort(key=lambda x: int(x.rendszerezes), reverse=True)
            
                
        elif rendezes == "Leárazás":
                shoes = [shoe for shoe in shoes if shoe.akcios_ár != "0"]

        
        if rendezes == "Random":
            random.shuffle(shoes)
        elif query == 'SALE' and rendezes != "Random":
            pass  
        elif query == "POPULAR" or rendezes != "Leárazás" or rendezes != "szinek":
            pass  
        else:
            random.shuffle(shoes)
        
        szinek = set()
        markak = set()
        meretek = set()
        for i in shoes:
            for x in i.méretek:
                if "A" not in x and "391" not in x and "1 /" not in x:
                    meretek.add(x)

            for x in szinek_alpha:
                 if x.lower() in i.name.lower():
                      szinek.add(x)
            for x in markak_alpha:
                 if x.lower() in i.name.lower():
                      markak.add(x)
        meretek = sorted(meretek)
        import math
        max_price = 500000
        shoes = list(shoes)
        arak = []
        for d in shoes:
             arak.append(int(d.price.replace(" ","")))
        
        
        db = len(shoes)
        page = request.GET.get('page', '')
        if page == "":
             jelenlegioldal = 1
             shoes = shoes[0:24]
             
        else:
            jelenlegioldal = page
            jelenlegioldal = int(jelenlegioldal)
        
            kezdo_index = (jelenlegioldal - 1) * 24    
        
            
            
            
            vegso_index = kezdo_index + 24
            
            
            shoes = shoes[kezdo_index:vegso_index]
        
        következőoldal = jelenlegioldal + 1
        előzőoldal = jelenlegioldal -1
        oldalak = db / 24
        oldalak = math.ceil(oldalak)
        
        

       
        márkák = Márka.objects.all()
       
        if arak == []:
             pass
             legmagasabbar = 0
             legalacsonyabbar = 0

        else:
            alar = min(arak)
            legalacsonyabbar = int(alar)
            
            
            legar = max(arak)
            
            legmagasabbar = int(legar)
        
        
        for cipő in shoes:
                if meret == "None":
                    
                    cipő.kiv_ár = cipő.price
                    
                    cipő.kiv_akcios_ár = cipő.akcios_ár
                else:
                    
                    cipő.kiv_ár = cipő.méret_ár.get(meret, None)
                    
                    cipő.kiv_akcios_ár = cipő.méret_akciosok.get(meret, None)
           
        context = {'shoes': shoes, 'márkák':márkák, 'best_shoes':best_shoes, 'szinek': szinek ,'q': query, 'db': db, 'oldalak': oldalak, 'jelenlegioldal':jelenlegioldal, "következőoldal":következőoldal, 'előzőoldal': előzőoldal, "max_price": max_price, 'markak': markak, 'legmagasabbar':legmagasabbar, 'legalacsonyabbar':legalacsonyabbar, 'rendezes_allow': rendezes_allow, 'szinszamok': szinszamok, 'osszes_x_lehet':osszes_x_lehet,'szinek_x':szinek_x, 'szin_url':szin_url , 'markaszamok': markaszamok, 'markak_x':markak_x, 'marka_url':marka_url, 'meretek': meretek, 'meret': meret}

        return render(request, 'sneakerek.html', context)
def gyk(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'gyk.html', context)
def wp(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'wp.html', context)
def looks(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'looks.html', context)
def ab(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'ab.html', context)
def pos(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'pos.html', context)
def term(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'term.html', context)
def contact(request):
    q = request.GET.get('q', '')
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'contact.html', context)
from django.http import JsonResponse
from django.views import View

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()  # Get the search query and remove leading/trailing spaces
        if query:
            shoes = Shoe.objects.all()
            shoes = shoes.exclude(name__icontains="Nike Dunk Low Next Nature Pale Coral")
            # Create a search filter using Q objects, splitting query into terms
            search_filter = Q()
            for term in query.lower().split():
                search_filter &= Q(name__icontains=term)  # All terms must be in the shoe name

            # Apply the search filter to the shoes queryset
            results = shoes.filter(search_filter).values('name', 'image', 'price', 'cég')

            # Convert queryset to list and shuffle the results
            results = list(results)
            random.shuffle(results)

            # Limit the results to 4 items
            results = results[:4]

            # Return the shuffled, limited results as JSON
            return JsonResponse(results, safe=False)
        
        # If no query is provided, return an empty list
        return JsonResponse([], safe=False)
