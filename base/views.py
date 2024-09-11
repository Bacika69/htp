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
import  urllib.parse
import random
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Q

def home(request):

    márkák = ['Nike', 'New Balance', 'Adidas', 'Air Jordan', 'Yeezy']

    for marka in márkák:
        Márka.objects.get_or_create(
            name = marka
            )
    népszerű_cipők = ['Nike Dunk', 'Air Jordan', 'Adidas Campus', 'Air Force', 'Yeezy', 'New Blanace 550']
    for shoe in népszerű_cipők:
        bestseller.objects.get_or_create(
            name = shoe
            )
            
    

    base_url_1 = "https://www.truetosole.hu/collections/sneaker?page={}&grid_list=grid-view"
    result = requests.get(base_url_1).text
    doc = BeautifulSoup(result, "html.parser")
    nav = doc.select_one("nav.pagination--container")
    szamolas = 0
    szam = int(nav.select("li")[-2].select_one("a").string)
    joar = []
    with requests.Session() as s:
            for b in range(1, 1 ): 
                url = base_url_1.format(b)
                result_ = s.get(url).text
                doc_ = BeautifulSoup(result_, "html.parser")
                ul_ = doc_.select_one("ul.productgrid--items.products-per-row-4")
                if ul_ is None:  
                    break
                li_ = ul_.find_all("li")  
                for i in li_:
                    img = i.select_one("img.productitem--image-primary")
                    src = img['src']
                    img2 = i.select_one("img.productitem--image-alternate")
                    try:
                        src2 = img2['src']
                    except:
                         src2 = "nincs"
                    név = i.find('h2', class_="productitem--title")
                    név = név.a
                    név = név.text.strip()
                    asd = i.select_one("div.price__current")
                    try:
                        asd2 = i.find("span", class_="money price__compare-at--min")
                        akcios = asd2.find("span", class_="mw-price")
                        akcios = akcios.string
                        akcios = akcios.replace("FT", "")

                    except:
                        pass
                    árak  = asd.find("span", class_="mw-price")
                    ár = árak.string
                    ár = ár.replace("FT", "")
                    if akcios <= ár:
                        akcios = 0
                    link = i.find('a', attrs={'data-product-page-link': True}) 
                    link = link["href"]
                    link = f"https://www.truetosole.hu{link}"
                    rendezes = re.sub(r'[^\d\s]', '', ár)
                    rendezes = rendezes.replace(" ", "")
                    rendezes = int(rendezes)
                    
                    
                    Shoe.objects.get_or_create(
                        name = név,
                        price = ár,
                        image = src,
                        image_2 = src2,
                        rendszerezes = rendezes,
                        cég = "TrueToSole",
                        link = link,
                        akcios_ár = akcios
                    )
                    szamolas += 1
    base_url = "https://balazskicks.com/collections/sneakerek?page={}"

    for a in range(1, 1):
        url = base_url.format(a)
        result = requests.get(url).text
        doc = BeautifulSoup(result, "html.parser")
        divs = doc.find_all('div', class_='product-card__info')
        if not divs:
            break
        nevek = []
        fotok = []
        fotok2 = []
        árak = []
        linkek = []
        akcios = []
        for cucc in divs:
            név = cucc.find('span', class_='product-card__title')
            név = név.a
            név = név.string
            ár = cucc.find_all('span', class_='tlab-currency-format')
            try:
                akcios_ár = ár[1]
                akcios_ár = akcios_ár.string
                akcios_ár = akcios_ár.split('.')
                akcios_ár = akcios_ár[0].replace(",", " ")
                akcios.append(akcios_ár)
            except:
                 akcios_ár = 0
                 akcios.append(akcios_ár)
            ár = ár[0]
            ár = ár.string
            ár = ár.split('.')
            ár = ár[0].replace(",", " ")
            rendezes = ár.replace(" ", "")
            árak.append(ár)
            nevek.append(név)
        foto_divs = doc.find_all('div', class_='product-card__figure')
        for kepstuff in foto_divs:
            a = kepstuff.a
            img = a.img
            src = img['src']
            link = a['href']
            try:
                img2 = a.find_all('img')
                img2 = img2[1]
                src2 = img2['src']
            except:
                 src2 = "nincs"
            fotok.append(src)
            fotok2.append(src2)
            linkek.append(link)
        cipők = list(zip(nevek, árak, fotok, fotok2, linkek, akcios))
        for cipő_dolgok in cipők:
            rendezes = cipő_dolgok[1]
            rendezes = rendezes.replace(" ", "")
            jo_link = cipő_dolgok[4]
            jo_link = f"https://balazskicks.com{jo_link}"
            Shoe.objects.get_or_create(
                        name = cipő_dolgok[0],
                        price = cipő_dolgok[1],
                        image = cipő_dolgok[2],
                        image_2 = cipő_dolgok[3],
                        rendszerezes = rendezes,
                        cég = "Balazskicks",
                        link = jo_link,
                        akcios_ár = cipő_dolgok[5]
                    )
    márka_sneak = ['nike', 'air-jordan', 'adidas', 'new-balance-1']
    nevek = []
    fotok = []
    fotok2=[]
    linkek = []
    árak = []
    akciosok = []
    for w in márka_sneak:
            for y in range(1, 1):
                url = f"https://sneakcenter.com/collections/{w}?page={y}"
                result = requests.get(url).text
                doc = BeautifulSoup(result, "html.parser")
                árak_span = doc.find_all('p', class_='product-item__price 4')
                if árak_span is None:
                    break
                for i in árak_span:
                    ár_ = i.find_all('span', class_='transcy-money')
                    if len(ár_) == 2:
                        ár = ár_[1]
                        akcios = ár_[0]
                        akcios = akcios.string
                        akcios = akcios.split('.')[0].replace(",", " ")
                        akciosok.append(akcios)
                    else:
                        ár = ár_[0]
                        akcios = 0
                        akciosok.append(akcios)
                    ár = ár.string
                    ár = ár.split('.')[0].replace(",", " ")
                    árak.append(ár)
                név_h4 = doc.find_all('h4', class_='ff-body product-item__product-title fs-product-card-title notranslate')
                for x in név_h4:
                    a = x.a                    
                    név = a.string
                    nevek.append(név)
                
                kep_as = doc.find_all('a', class_='product-item__image-link')
                for kep_div in kep_as:
                        link = kep_div['href']
                        link = f"https://sneakcenter.com/{link}"
                        div = kep_div.div
                        img = div.img
                        src = img['src']
                        try:
                            div2 = kep_div.find_all('div')
                            div2 = div2[1]
                            img2 = div2.img
                            src2 = img2['src']
                        except:
                            src2 = "nincs"
                        fotok.append(src)
                        fotok2.append(src2)
                        linkek.append(link)

    cipők = list(zip(nevek, árak, fotok, fotok2, linkek, akciosok))  
    for cipő_dolgok in cipők:
        rendezes = cipő_dolgok[1].replace(" ", "")
        Shoe.objects.get_or_create(
                            name = cipő_dolgok[0],
                            price = cipő_dolgok[1],
                            image = cipő_dolgok[2],
                            image_2 = cipő_dolgok[3],
                            rendszerezes = rendezes,
                            cég = "Sneakercenter",
                            link = cipő_dolgok[4],
                            akcios_ár = cipő_dolgok[5]
                        )
    base_url_2 = "https://onsize.eu/collections/sneakerek?page={}"

    nevek = []
    árak = []
    fotók = []
    fotok2 = []
    akciosokok = []
    linkek = []

    for i in range(1, 1):
            url = base_url_2.format(i)
            result = requests.get(url).text
            doc = BeautifulSoup(result, "html.parser")
            divs = doc.find_all('product-card')
            for product in divs:
                név = product.find('span', class_='product-card__title')
                if not név:
                    break
                név = név.a
                név = név.string
                
                ár = product.find('sale-price')
                ár = ár.find_all('span')
                ár = ár[1]
                ár = ár.string
                ár = ár.replace("Ft", "")
                ár = ár.replace(" ", "")
                ár = int(ár)
                ár = '{:,}'.format(ár)
                ár = ár.replace(",", " ")
                try:
                    akciosár = product.find('compare-at-price')
                    akciosár = akciosár.find_all('span')
                    akciosár = akciosár[1]
                    akciosár = akciosár.string
                    akciosár = akciosár.replace("Ft", "")
                    akciosár = akciosár.replace(" ", "")
                    akciosár = int(akciosár)
                    akciosár = '{:,}'.format(akciosár)
                    akciosár = akciosár.replace(",", " ")
                except:
                    akciosár = 0
                kép = product.find('div', class_="product-card__figure")
                kép = kép.a
                link = kép['href']
                link = f"https://onsize.eu{link}"
                imgk = kép.find_all('img')
                if len(imgk) == 1:
                        pass
                else:
                        kép = imgk[1]
                        try:
                            kép_2 = imgk[0]
                            kép_2 = kép_2['src']
                            kép = kép['src']
                        except:
                            kép_2 = "nincs"
                        fotók.append(kép)
                        fotok2.append(kép_2)
                        linkek.append(link)
                        árak.append(ár)
                        nevek.append(név)
                        akciosokok.append(akciosár)
    cipők = list(zip(nevek, árak, fotók, fotok2, linkek, akciosokok))
    for cipő_dolgok in cipők:
        rendezes = cipő_dolgok[1].replace(" ", "")
        Shoe.objects.get_or_create(
                            name = cipő_dolgok[0],
                            price = cipő_dolgok[1],
                            image = cipő_dolgok[2],
                            image_2 = cipő_dolgok[3],
                            rendszerezes = rendezes,
                            cég = "OnSize",
                            link = cipő_dolgok[4],
                            akcios_ár = cipő_dolgok[5]
                        )
    
    base_url_3 = "https://www.rdrop.hu/collections/osszes-sneaker?page={}"


    for i in range(1, 0):
        

        url = base_url_3.format(i)
        result = requests.get(url).text
        doc = BeautifulSoup(result, "html.parser")
        lis = doc.find_all('li', class_='grid__item')
        if not lis:
            break
        for q in lis:
            név = q.find('h3', class_='card__heading h5')
            név = név.a
            href = név['href']
            href = f"https://www.rdrop.hu/{href}"
            név = név.string
            név = név.lstrip()
            if "(ENFANT)" or "(NOIR)" in név:
                név = név.replace("(ENFANT)", "")
                név = név.replace("(NOIR)", "")
            név = név.title()
            ár = q.find('span', class_="price-item price-item--sale price-item--last")
            ár = ár.string
            ár = ár.split('Ft')
            ár = ár[0]
            ár = ár.replace('.', ' ')
            ár = ár.replace(' ', '')
            ár = int(ár)
            ár = '{:,}'.format(ár)
            ár = ár.replace(",", " ")
            rendezes = ár.replace(" ", "")
            try:
                akciosár = q.find('s', class_="price-item price-item--regular")
                akciosár = akciosár.string
                akciosár = akciosár.split('Ft')
                akciosár = akciosár[0]
                akciosár = akciosár.replace('.', ' ')
                akciosár = akciosár.replace(' ', '')
                akciosár = int(akciosár)
                akciosár = '{:,}'.format(akciosár)
                akciosár = akciosár.replace(",", " ")
                if akciosár < ár or akciosár == ár:
                     akciosár = 0
                
            except:
                 akciosár = 0
            
            kép = q.find('div', class_="media media--transparent media--hover-effect")
            try:
                kép2 = kép.find_all('img')
                kép2 = kép2[1]
                kép2 = kép2['src']
            except:
                 kép2 = "nincs"
            kép = kép.img
            kép = kép['src']
            név = név.strip()
            Shoe.objects.get_or_create(
                            name = név,
                            price = ár,
                            image = kép,
                            image_2 = kép2,
                            rendszerezes = rendezes,
                            cég = "Rdrop",
                            link = href,
                            akcios_ár = akciosár
                        )

    # service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)
    # link = "https://www.footshop.hu/hu/4600-ferfi-sneakerek/page-{}"
    # for szam in range(0, 0):
    #     if szam != 1:
    #         url = link.format(szam)
    #         driver.get(url)
    #         source = driver.page_source
    #         soup = BeautifulSoup(source, 'html.parser')
    #         try:
    #             cookie = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "cbButton.cbButtonPrimary")))
    #             cookie.click()
    #         except:
    #             pass

    #         nevek = []
    #         árak = []
    #         linkek = []
    #         fotók = []
    #         try: 
    #             cipő_nevek = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "Product_name_1Go7D")))
    #         except TimeoutException:
    #             break
    #         for cipő in cipő_nevek:
    #             név = cipő.text
    #             nevek.append(név)
    #         cipő_árak = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class*='ProductPrice_price_J4pAM']")))
    #         for i in cipő_árak:
    #             ár = i.text
    #             if "\n" in ár:
    #                 ár = ár.split("\n")[0]
    #             else:
    #                 pass
    #             árak.append(ár)
    #         links =  WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"Product_inner_1kysz")))
    #         for q in links:
    #             link_ = q.find_element(By.TAG_NAME, "a")
    #             link_ = link_.get_attribute("href")
    #             linkek.append(link_)
    #         kép_divs = soup.find_all('div', class_='Products_product_1JtLQ')

    #         for div in kép_divs:
    #             img = div.find('meta', itemprop="image")
    #             src = img['content']
    #             fotók.append(src)
    #             print(src)
    #         cipők = list(zip(nevek, árak, linkek, fotók))
    #         for cipő_dolgok in cipők:
    #             ár = cipő_dolgok[1]
    #             ár = str(ár)
    #             ár = ár.replace("Ft", "")
    #             rendezes = ár.replace(" ", "")
    #             rendezes = int(rendezes)
    #             Shoe.objects.get_or_create(
    #                     name = cipő_dolgok[0],
    #                     price = ár,
    #                     image = cipő_dolgok[3],
    #                     rendszerezes = rendezes,
    #                     cég = "footshop",
    #                     link = cipő_dolgok[2],
    #                 )
            
    # driver.quit() 

    # service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)


    # link = "https://sizeer.hu/ferfi/cipo?page={}"



    # for szam in range(1, 1):
        
    #         url = link.format(szam)
    #         driver.get(url)
            
    #         # try:
    #         #     cookie = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
    #         #     cookie.click()
    #         # except:
    #         #     pass
    #         nevek = []
    #         árak = []
    #         fotók = []
    #         linkek = []
    #         start_ido = datetime.datetime.now()  


    #         for i in range(1000000):

    #             WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.PAGE_DOWN)

    #             jelenidő = datetime.datetime.now()
    #             elteltidő = jelenidő - start_ido

    #             if elteltidő.total_seconds() >= 3:  
    #                 break
    #         source = driver.page_source
    #         soup = BeautifulSoup(source, 'html.parser')
    #         try: 
    #             cipő_nevek = WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "b-itemList_nameLink")))
    #         except TimeoutException:
    #             break
                
            
    #         ár_divs = soup.find_all('div', class_='b-itemList_prices js-offer-price is-omnibus')
            
    #         for z in ár_divs:
    #             p_k = z.find_all('p')
    #             if len(p_k) == 2:
    #                 ár = p_k[1]
    #             else: 
    #                 ár = p_k[0]
    #             ár = ár.string
    #             ár = ár.replace("FT", "")
    #             ár = ár.replace(" ", "")
                # ár = int(ár)
                # ár = '{:,}'.format(ár)
                # ár = ár.replace(",", " ")
    #             árak.append(ár)

    #         for cipő in cipő_nevek:
    #             név = cipő.text
    #             név_link = cipő.get_attribute("href")
    #             linkek.append(név_link)
    #             nevek.append(név)
            
    #         kep_divs = soup.find_all('a', class_='b-itemList_photoLink')
    #         for x in kep_divs:
    #             kép = x.img
    #             kép = kép['src']
    #             kép = f"https://sizeer.hu{kép}"
    #             fotók.append(kép)

    #         cipők = list(zip(nevek, árak, fotók, linkek))
            
    #         for cipő_dolgok in cipők:
    #             rendezes = cipő_dolgok[1]
    #             rendezes = rendezes.replace(" ", "")
    #             Shoe.objects.get_or_create(
    #                         name = cipő_dolgok[0],
    #                         price = cipő_dolgok[1],
    #                         image = cipő_dolgok[2],
    #                         rendszerezes = rendezes,
    #                         cég = "sizeer",
    #                         link = cipő_dolgok[3],
    #                     )


    # driver.quit() 
    # service = Service(executable_path="chromedriver.exe")
    # driver = webdriver.Chrome(service=service)

    # url = "https://www.footlocker.hu/en/category/men/shoes/sneakers.html?currentPage=0"
    # szam = 0
    # driver.get(url)
    # while szam != 23:

    #     nevek = []
    #     árak = []
    #     fotók = []
    #     linkek = []
        
    #     try:
    #         cookie = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler")))
    #         cookie.click()
    #     except:
    #         pass
    #     try: 
    #         next_gomb = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Next")))
    #     except TimeoutException:
    #         break
    #     source = driver.page_source
    #     soup = BeautifulSoup(source, 'html.parser')
    #     cipő_nevek = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductName-primary")))
    #     cipő_árak = soup.find_all('span', "ProductPrice")    
    #     cipő_fotók = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard-image")))
    #     cipő_linkek = soup.find_all('a', "ProductCard-link ProductCard-content")

    #     for név, lehetseges_ár, fotó, link in zip(cipő_nevek, cipő_árak, cipő_fotók, cipő_linkek):
    #         ár = lehetseges_ár.text
    #         ár = ár.split(",")
    #         ár = ár[0]
    #         ár = ár.replace("Ft", "")
    #         ár = ár.replace(" ", "")
    #         try:
    #             ár = int(ár)
    #             ár = '{:,}'.format(ár)
    #             ár = ár.replace(",", " ")
    #         except:
    #             ár = lehetseges_ár.find('span', "ProductPrice-final")
    #             ár = ár.string
    #             ár = ár.split(",")
    #             ár = ár[0]
    #             ár = ár.replace("Ft", "")
    #             ár = ár.replace(" ", "")
    #             ár = int(ár)
    #             ár = '{:,}'.format(ár)
    #             ár = ár.replace(",", " ")
    #         név = név.text
    #         img_element = fotó.find_element(By.TAG_NAME, "img")
    #         fotó = img_element.get_attribute("src")
    #         link = link['href']
    #         link = f"https://www.footlocker.hu{link}"
    #         nevek.append(név)
    #         árak.append(ár)
    #         fotók.append(fotó)
    #         linkek.append(link)
    
    #     cipők = list(zip(nevek, árak, fotók, linkek))
    #     for cipő_dolgok in cipők:
    #         rendezes = cipő_dolgok[1].replace(" ", "")
    #         Shoe.objects.get_or_create(
    #                         name = cipő_dolgok[0],
    #                         price = cipő_dolgok[1],
    #                         image = cipő_dolgok[2],
    #                         rendszerezes = rendezes,
    #                         cég = "Foot Locker",
    #                         link = cipő_dolgok[3],
    #                     )
    #     if szam != 9:
    #         next_gomb.click()
    #     else:
    #         break
    #     szam = szam + 1

    # driver.quit()
    # cipők = {'NIKE DUNK': [], 'AIR JORDAN': [], 'NEW BALANCE 550': [], 'AIR FORCE': [], 'ADIDAS CAMPUS': [], 'ADIDAS YEEZY': []}
    # márkák = Márka.objects.all()
    # shoes = Shoe.objects.all()
    # shoes = shoes.exclude(name__icontains="(TD & PS)")
    # shoes = shoes.exclude(name__icontains="(Infants)")
    # shoes = list(shoes)
    # random.shuffle(shoes)
    # for cipő in shoes:
    #     cipő_név = cipő.name.lower()
    #     if 'dunk' in cipő_név:
    #         cipők['NIKE DUNK'].append(cipő)
    #     elif 'jordan' in cipő_név:
    #         cipők['AIR JORDAN'].append(cipő)
    #     elif '550' in cipő_név:
    #         cipők['NEW BALANCE 550'].append(cipő)
    #     elif 'air force' in cipő_név:
    #         cipők['AIR FORCE'].append(cipő)
    #     elif 'campus' in cipő_név:
    #         cipők['ADIDAS CAMPUS'].append(cipő)
    #     elif 'yeezy' in cipő_név:
    #         cipők['ADIDAS YEEZY'].append(cipő)
    cipők = {'SALE': [],'POPULAR': []}
    shoes = Shoe.objects.all()
    shoes = shoes.exclude(name__icontains="(TD & PS)")
    shoes = shoes.exclude(name__icontains="(Infants)")
    shoes = shoes.exclude(name__icontains="(TD)")
    shoes = list(shoes)
    random.shuffle(shoes)
    while True:
        szam = 0
        for cipő in shoes:
            if szam == 16:
                break
            if cipő.akcios_ár != "0":
                cipők['SALE'].append(cipő)
                szam = szam + 1
        break
    
    while True:
        szam = 0
        for cipő in shoes:
            if szam == 16:
                break
            if '00s grey white' in cipő.name.lower() or '00s core black' in cipő.name.lower() or 'low 07 triple white' in cipő.name.lower() or 'military black' in cipő.name.lower() or 'thunder' in cipő.name.lower() or 'mid panda' in cipő.name.lower():
                cipők['POPULAR'].append(cipő)
                szam = szam + 1
        break
    q = request.GET.get('q', '')
    
    if q == '':
        q = None
        length = '2'
    
    else:
        
        print(q)
        q = q.lower()
        
        q = q.replace("'", "")
        q = q.replace('"', "")
        q = q.replace('gs', "")
        q = q.replace("(w)", "")
        q = q.replace("(", "")
        q = q.replace(")", "")
        # q = re.sub(r'\([^)]*\)', '', q)
        q = q.replace("2023", "")
        q = q.replace("2021", "")
        q = q.replace("2022", "")
        q = q.replace("rnnr", "runner")
        q = q.replace("rnr", "runner")
        q = q.strip()
        q_egesz = q
        q = q.split(' ')
        
        if len(q) < 7:
            print("kis")
            q = f"{q[1]} {q[2]} {q[-2]} {q[-1]}"
            match_szam = 4
        else:
            q = f"{q[1]} {q[2]} {q[3]} {q[-3]} {q[-2]} {q[-1]}"
            match_szam = 6
        print(q)
        cipők = []
        
        shoes__ = Shoe.objects.all()
        shoes__ = shoes__.exclude(name__icontains="(TD & PS)")
        shoes__ = shoes__.exclude(name__icontains="(Infants)")
        shoes__ = shoes__.exclude(name__icontains="(TD)")
            
        for shoe_ in shoes__:
                # if '&' in shoe_.name:
                #     print("&")
                #     név_filter = shoe_.name.lower()
                #     név_filter = név_filter.split('&')
                #     név_filter = név_filter[0]
                #     match_count = 0
                #     for word in q.split(' '):
                #         if word in név_filter:
                #             match_count += 1
                    
                #     if match_count == match_szam:
                #         cipők.append(shoe_)
                # else:
                    shoe_name = shoe_.name.lower()
                    shoe_name = shoe_name.replace("'", "")
                    shoe_name = shoe_name.replace('gs', "")
                    shoe_name = shoe_name.replace('"', "")
                    shoe_name = shoe_name.replace("2023", "")
                    shoe_name = shoe_name.replace("2021", "")
                    shoe_name = shoe_name.replace("2022", "")
                    shoe_name = shoe_name.replace("(", "")
                    shoe_name = shoe_name.replace(")", "")
                    shoe_name = shoe_name.replace("rnnr", "runner")
                    shoe_name = shoe_name.replace("rnr", "runner")
                    # shoe_name = re.sub(r'\([^)]*\)', '', shoe_name)
                    
                    match_count = 0
                    for word in q.split(' '):
                        if word in shoe_name:
                            match_count += 1
                    szürö_szavak = ["black", "away", "og", "supreme", "charms", "state","sail", "mint", "nightwatch", "jackpot", "white", "red", "yellow","grey","light", "blue", "green", "orange", "prm", "pink","dark", "beige", "high", "alternate", "low", "mid", "navy","arctic", "mirage", "reverse", "elephant", "rope"]
                    if match_count == match_szam:
                        print()
                        print()
                        print(q_egesz)
                        print(shoe_name)
                        stim_szavak1 =[]
                        print()
                        
                        for ű in shoe_name.split():
                            if ű in szürö_szavak:
                                stim_szavak1.append(ű)
                        stim_szavak2  = []
                        print(stim_szavak1)
                        for ő in q_egesz.split(' '):
                            if ő in szürö_szavak:
                                stim_szavak2.append(ő)
                        print(stim_szavak2)
                        szam1 = len(stim_szavak1)
                        szam3 = len(stim_szavak2)
                        szam2 = 0
                        if szam1 == szam3:
                            for í in stim_szavak1:
                                if í in stim_szavak2:
                                    szam2 += 1
                            if szam1 == szam2:
                                cipők.append(shoe_)
                    
        
        cipők = list(cipők)
        random.shuffle(cipők)
        length=len(cipők)
        if length == 1:
            cipő = cipők[0]
            return redirect(reverse('room', kwargs={'pk': cipő.id}))
        
        print(cipők)
    
    
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}

    
    context = {'shoes': cipők,  'márkák': márkák, 'best_shoes': best_shoes, 'q': q, 'length': length}

    return render(request, 'home.html', context)

def room(request, pk):
    
    shoe = Shoe.objects.get(id=pk) 
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'shoe': shoe, 'best_shoes':best_shoes}

    return render(request, 'room.html', context)

def sneakerek(request): 
        shoes = Shoe.objects.all()
        shoes = shoes.exclude(name__icontains="(TD & PS)")
        shoes = shoes.exclude(name__icontains="(Infants)")
        shoes = shoes.exclude(name__icontains="(TD)")
        best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}

        query = request.GET.get('q', '') 
        print(query)
        rendezes = request.GET.get('r', '')
        if query == 'SALE':
            shoes = shoes.filter(akcios_ár__gt=0)
        elif query == 'POPULAR':
            shoes = shoes.filter(name__icontains='00s Grey White') | shoes.filter(name__icontains='00s Core Black') | shoes.filter(name__icontains='Military Black') | shoes.filter(name__icontains='Thunder') | shoes.filter(name__icontains='07 triple white') | shoes.filter(name__icontains='mid panda')
        else:
            search_filter = Q()
            for term in query.lower().split():
                search_filter &= Q(name__icontains=term)
            shoes = shoes.filter(search_filter)

            



        szinek = ['White', 'Black', 'Grey', 'Brown', 'Red', 'Orange', 'Blue', 'Green', 'Pink', 'Yellow']
            
        
        if rendezes == "Legalacsonyabb ár":
            shoes = shoes.order_by('rendszerezes')
        elif rendezes == "Legmagasabb ár":
            shoes = shoes.order_by('-rendszerezes')
        elif rendezes in szinek:
            shoes = shoes.filter(name__icontains=rendezes)
        elif rendezes == "Leárazás":
            shoes = shoes.filter(akcios_ár__gt=0)
        else:
            shoes = list(shoes)
            random.shuffle(shoes)
        shoes = list(shoes)
        db = len(shoes)
        márkák = Márka.objects.all()
        print(db)


        context = {'shoes': shoes, 'márkák':márkák, 'best_shoes':best_shoes, 'szinek': szinek ,'q': query, 'db': db}

        return render(request, 'sneakerek.html', context)
def gyk(request):
    q = request.GET.get('q', '')
    print(q)
    best_shoes = {'Nike': ["Air Force 1", "Air Max 1", "Dunk High", "Dunk Low"], 'Air Jordan': ["Air Jordan 1 High", "Air Jordan 1 Mid", "Air Jordan 1 Low", "Air Jordan 3", "Air Jordan 4"],
                    'Adidas': ["Adidas Campus", "Adidas Gazelle", "Adidas Samba"], 'Yeezy': ["Yeezy Boost 350", "Yeezy Slide", "Yeezy Foam"], 'New Balance': ["New Balance 550", "New Balance 2002R", "New Balance 9060"]}
    context = {'best_shoes': best_shoes, 'q':q}
    return render(request, 'gyk.html', context)
from django.http import JsonResponse
from django.views import View

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()  # Get the search query and remove leading/trailing spaces
        if query:
            shoes = Shoe.objects.all()

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