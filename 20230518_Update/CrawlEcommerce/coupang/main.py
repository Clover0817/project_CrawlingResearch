import os
import subprocess
import mysql.connector
import chromedriver_autoinstaller
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import loginInfo, dbInfo

class Coupang:
    def __init__(self, url, login_mode, os_mode): 
        #초기화
        self.url = url
        self.login_mode = login_mode
        self.os_mode = os_mode
        
        #Driver 연결
        if self.os_mode == 0:
            import shutil
            try:
                shutil.rmtree(r"c:\chrometemp")  #쿠키 / 캐쉬파일 삭제
            except FileNotFoundError:
                pass

            subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"') # 디버거 크롬 구동


            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            try:
                self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
            except:
                chromedriver_autoinstaller.install(True)
                self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=option)
            self.driver.implicitly_wait(10)

        elif self.os_mode == 1:
            subprocess.Popen(f'google-chrome --remote-debugging-port=9222  --user-data-dir=data_dir'.split()) 
            chrome_option = Options()
            chrome_option.add_argument('headless')
            chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            try:
                self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
            except:
                chromedriver_autoinstaller.install(True)

            self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
            self.driver.implicitly_wait(10)

        #DB 연결
        db = dbInfo.insertInfo(0)
        self.dbconn = mysql.connector.connect(host=db['host'], user=db['user'], password=db['password'], db=db['db'], port=db['port'])
        self.cursor = self.dbconn.cursor(buffered=True)
        self.CoupangData = CoupangData(self.url, self.dbconn, self.cursor, self.driver)

        #로그인 여부
        if self.login_mode == 1:
            CoupangData.login(self.driver)

    def search(self):
        self.CoupangData.total_ads()
        self.dbconn.close()
        self.driver.quit()
 
    def best(self):
        self.CoupangData.total_best()
        self.dbconn.close()
        self.driver.quit()
        
    def event(self):
        self.CoupangData.total_event()
        self.dbconn.close() 
        self.driver.quit()

    def category(self):
        self.CoupangData.total_category()
        self.dbconn.close()
        self.driver.quit()

    def review(self):
        self.CoupangData.total_review()
        self.dbconn.close()
        self.driver.quit()
          

class CoupangData:
    def __init__(self, url, dbconn, cursor, driver) : 
        #초기화
        self.url = url
        self.dbconn = dbconn
        self.cursor = cursor
        self.driver = driver
    
    def login(driver):
        driver.get('https://login.coupang.com/login/login.pang')
        driver.implicitly_wait(5)

        id, password = loginInfo.login(0) #site_option = 0

        id_input = driver.find_element(By.XPATH, '//*[@id="login-email-input"]')
        id_input.send_keys(id)

        pw_input = driver.find_element(By.XPATH, '//*[@id="login-password-input"]')
        pw_input.send_keys(password)

        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div[5]/button').click()
        driver.implicitly_wait(10)
        
    def total_ads(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('coupang_ads.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("coupang_ads.html", "w")
            f.write(soup.prettify())
            f.close()

        #정보 크롤링
        ul = self.driver.find_element(By.XPATH, '//*[@id="productList"]')
        lis = ul.find_elements(By.XPATH, './/li')
        i = 1
        for li in lis:
            data = {}
            try: 
                id = li.get_attribute("id")
                productNo = id
                adsYn = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/span/span[1]')
                adsYn = 'Y'

                productName = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[2]').text
                try:
                    listPrice = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/span[1]/del').text
                    listPrice = listPrice.replace(',', '')
                    listPrice = (int)(listPrice, base=0)
                except NoSuchElementException:
                    listPrice = 0

                price = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
                try:
                    price = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
                    price = price.replace(',', '')
                    price = (int)(price, base=0)
                except NoSuchElementException:
                    price = 0
            
                discountProvider = 0
                discountPriceCommerce = 0
                discountCouponName = 'sale'
                discountDouble = 0
                try:
                    discountRateDouble = self.driver.find_element(By.CLASS_NAME, 'instant-discount-rate').text
                    discountRateDouble = discountRateDouble.replace('%', '')
                    discountRateDouble = int(discountRateDouble, base=0)
                except NoSuchElementException:
                    discountRateDouble = 0
                discountCouponNameDouble = '알 수 없음'
                totalPrice = price
                bestRank = -1
                try:
                    starScore = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[4]/div/span[1]/em').text
                    starScore = (float)(starScore)
                except NoSuchElementException:
                    starScore = 0
                reviewCount = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[4]/div/span[2]').text
                reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                reviewCount = (int)(reviewCount, base=0)
                buyCount = 0
                saleCompany = 'COUPANG'
                deliveryPrice = 0
                productUrl = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a').get_attribute('href')
                deliveryType = "로켓배송"
                searchWord = self.driver.find_element(By.XPATH, '//*[@id="searchOptionForm"]/input[3]').get_attribute('value')
                adArea = '상품리스트'
                optionName = '알 수 없음'
                likeClick = 0
                salesMan = 'COUPANG'
                optionNo = 0
                brandName = '알 수 없음'
                event = '없음'
                vendorItemId = li.get_attribute("data-vendor-item-id")
                collectionDate = datetime.now()
                commerceType = 'COUPANG'
                created = datetime.now()
                updated = datetime.now()
                updater = 1
                etcDeliveryName = '알 수 없음'
                referenceId = 0
                productCategory = self.driver.find_element(By.XPATH, '//*[@id="searchCategoryComponent"]/ul/li[1]/label').text
                dataRanking = i
                creator = 1

                data = {
                    'product_name': productName,
                    'product_no':productNo,
                    'list_price': listPrice,
                    'price':price,
                    'discount_provider':discountProvider,
                    'discount_price_commerce': discountPriceCommerce,
                    'discount_coupon_name':discountCouponName,
                    'discount_double':discountDouble,
                    'discount_rate_double':discountRateDouble,
                    'discount_coupon_name_double':discountCouponNameDouble,
                    'total_price':totalPrice,
                    'best_rank':bestRank,
                    'star_score':starScore,
                    'review_count':reviewCount,
                    'buy_count':buyCount,
                    'sale_company':saleCompany,
                    'delivery_price':deliveryPrice,
                    'product_url':productUrl,
                    'delivery_type':deliveryType,
                    'search_word':searchWord,
                    'ad_area':adArea,
                    'option_name':optionName,
                    'like_click':likeClick,
                    'salesman':salesMan,
                    'option_no':optionNo,
                    'brand_name':brandName,
                    'event':event,
                    'vendor_item_id':vendorItemId,
                    'collection_date':collectionDate,
                    'commerce_type':commerceType,
                    'created':created,
                    'updated':updated,
                    'updater':updater,
                    'etc_delivery_name':etcDeliveryName,
                    'reference_id':referenceId,
                    'product_category':productCategory,
                    'ads_yn':adsYn,
                    'data_ranking':dataRanking,
                    'creator':creator
                }

                i += 1
                dbInfo.insert_data("total_ads", self.dbconn, self.cursor, data)

            except NoSuchElementException:
                continue

    def total_best(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('coupang_best.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("coupang_best.html", "w")
            f.write(soup.prettify())
            f.close()

        #정보 크롤링
        list = self.driver.find_element(By.XPATH, '//*[@id="productList"]')
        lis = list.find_elements(By.XPATH, './/li')

        i = 1
        for li in lis:
            data = {}
            productUrl = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').get_attribute('href')

            productName = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[2]').text
            deliveryType = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[3]/div/div[3]/span').text
            discountCouponName = '없음'
            totalPrice = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
            totalPrice = totalPrice.replace(',', '')
            totalPrice = (int)(totalPrice, base=0)
            productOption = '없음'
            event = '없음'
            self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').click()
            self.driver.implicitly_wait(5)

            self.driver.switch_to.window(self.driver.window_handles[-1]) 
            try:
                listPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[2]/span[1]/strong').text
                listPrice = listPrice.replace(',', '').replace('원', '')
                listPrice = (int)(listPrice, base=0)
            except NoSuchElementException:
                listPrice = 0
            productNo = self.driver.find_element(By.XPATH, '//*[@id="contents"]').get_attribute("data-product-id")
            try:
                price = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[3]/span[1]/strong').text
                price = price.replace(',', '').replace('원', '')
                price = (int)(price, base=0)
            except NoSuchElementException:
                price = 0
        
            discountRate = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRate = discountRate.replace('%', '')
            discountRate = (float)(int(discountRate, base=0))/100
            discountPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[2]').text
            discountRateCommerce = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRateCommerce = discountRateCommerce.replace('%', '')
            discountRateCommerce = float(int(discountRateCommerce, base=0))/100
            discountCouponName = '쿠폰'
            discountDouble = '알 수 없음'
            discountRateDouble = '알 수 없음'
            discountCouponNameDouble = '알 수 없음'
            bestRank = -1
            starScore = self.driver.find_element(By.XPATH, '//*[@id="prod-review-nav-link"]/span[1]/span').get_attribute('style')
            import re
            width = re.search(r"width:\s*(\d+)", starScore)
            if width:
                widthVal = width.group(1)
            else:
                widthVal = None
            widthVal = widthVal.replace('%', '')
            widthVal = (float)(int(widthVal, base=0)) / 20
            self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]').click()
            self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[1]/div[3]/span').click()
            starScoreBestRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[2]/div[3]').text
            starScoreBestRate = starScoreBestRate.replace('%', '')
            starScoreBestRate = (float)(int(starScoreBestRate, base=0))/100
            starScoreGoodRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[3]/div[3]').text
            starScoreGoodRate = starScoreGoodRate.replace('%', '')
            starScoreGoodRate = (float)(int(starScoreGoodRate, base=0))/100
            starScoreBadRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[5]/div[3]').text
            starScoreBadRate = starScoreBadRate.replace('%', '')
            starScoreBadRate = (float)(int(starScoreBadRate, base=0))/100
            starScoreWorstRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[6]/div[3]').text
            starScoreWorstRate = starScoreWorstRate.replace('%', '')
            starScoreWorstRate = (float)(int(starScoreWorstRate, base=0))/100
            reviewCount = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]/span').text
            reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
            reviewCount = (int)(reviewCount, base=0)
            buyCount = 0
            saleCompany = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/a').text
            try:
                deliveryPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[7]/div[3]/div[1]/div[1]/div[1]/span/em[1]').text
                if (deliveryPrice == '무료배송'):
                    deliveryPrice = 0
                else:
                    deliveryPrice = deliveryPrice[4:]
                    deliveryPrice = deliveryPrice.replace('원', '')
                    deliveryPrice = (int)(deliveryPrice,base=0)
            except NoSuchElementException:
                deliveryPrice = -1
            collect = '수집완료'
            brandName = saleCompany
            category = self.driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[2]/a').text
            venderItemId = '알 수 없음'
            dealProjectName = event
            dealNo = i
            storeFriend = '알 수 없음'
            likeCount = 0
            priceUnit = 0
            division = self.driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[3]/a').text
            created = datetime.now()
            updated = datetime.now()
            updater = 'root'
            collection_date = datetime.now()
            commerceType = 'COUPANG'
            discountProvider = 0
            discountPriceCommerce = 0
            etcDeliveryName = ''
            searchWord = '행사'
            adsYn = 'Y'
            url = productUrl
            creator = 0

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            data = {
                'product_no': productNo,
                'product_name':productName,
                'list_price': listPrice,
                'price':price,
                'discount_rate':discountRate,
                'discount_price': discountPrice,
                'discount_rate_commerce':discountRateCommerce,
                'discount_coupon_name':discountCouponName,
                'discount_double':discountDouble,
                'discount_rate_double':discountRateDouble,
                'discount_coupon_name_double':discountCouponNameDouble,
                'total_price':totalPrice,
                'best_rank':bestRank,
                'star_score':starScore,
                'star_score_best_rate':starScoreBestRate,
                'star_score_good_rate':starScoreGoodRate,
                'star_score_bad_rate':starScoreBadRate,
                'star_score_worst_rate':starScoreWorstRate,
                'review_count':reviewCount,
                'buy_count':buyCount,
                'sale_company':saleCompany,
                'delivery_price':deliveryPrice,
                'product_url':productUrl,
                'product_option':productOption,
                'delivery_type':deliveryType,
                'collect':collect,
                'brand_name':brandName,
                'category':category,
                'vendor_item_id':venderItemId,
                'event':event,
                'deal_project_name':dealProjectName,
                'deal_no':dealNo,
                'store_friend':storeFriend,
                'like_count':likeCount,
                'price_unit':priceUnit,
                'division':division,
                'created':created,
                'updated':updated,
                'updater':updater,
                'collection_date':collection_date,
                'commerce_type':commerceType,
                'discount_provider':discountProvider,
                'discount_price_commerce':discountPriceCommerce,
                'etc_delivery_name':etcDeliveryName,
                'search_word':searchWord,
                'ads_yn':adsYn,
                'url':url,
                'creator':creator
            }

            i += 1
            dbInfo.insert_data(self.dbconn, self.cursor, data)


    def total_event(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('coupang_event.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("coupang_event.html", "w")
            f.write(soup.prettify())
            f.close()

        #정보 크롤링
        div = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div/div')
        list = div.find_element(By.XPATH, '//*[@id="productList"]')
        lis = list.find_elements(By.XPATH, '//*[@id="productList"]/li')

        i = 1
        for li in lis:
            data = {}
            img = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/img').get_attribute('src')
            productUrl = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').get_attribute('href')

            self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').click()
            self.driver.implicitly_wait(5)

            productName = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[1]/a/div[2]/h3').text
            deliveryType = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[1]/a/div[2]/div[4]/em[1]').text
            discountCouponName = self.driver.find_element(By.XPATH, '//*[@id="eventSort"]').text
            totalPrice = self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[1]/a/div[2]/div[3]/div/div/span').text
            totalPrice = totalPrice.replace(',', '')
            totalPrice = (int)(totalPrice, base=0)
            productOption = self.driver.find_element(By.XPATH, '//*[@id="eventCondition"]').text
            event = self.driver.find_element(By.XPATH, '//*[@id="promotionName"]').text
            self.driver.find_element(By.XPATH, '//*[@id="productList"]/li[1]/a/div[2]/h3').click()
            self.driver.implicitly_wait(5)

            self.driver.switch_to.window(self.driver.window_handles[-1]) 
            try:
                listPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[2]/span[1]/strong').text
            except NoSuchElementException:
                listPrice = 0
            productNo = self.driver.find_element(By.XPATH, '//*[@id="contents"]').get_attribute("data-product-id")
            try:
                price = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[3]/span[1]/strong').text
                price = price.replace(',', '').replace('원', '')
                price = (int)(price, base=0)
            except NoSuchElementException:
                price = 0
        
            discountRate = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRate = discountRate.replace('%', '')
            discountRate = (float)(int(discountRate, base=0))/100
            discountPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[2]').text
            discountPrice = discountPrice.replace(',', '').replace('원', '')
            discountPrice = (int)(discountPrice, base=0)
            discountRateCommerce = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRateCommerce = discountRateCommerce.replace('%', '')
            discountRateCommerce = float(int(discountRateCommerce, base=0))/100
            discountCouponName = img
            discountDouble = '알 수 없음'
            discountRateDouble = '알 수 없음'
            discountCouponNameDouble = '알 수 없음'
            bestRank = -1
            starScore = self.driver.find_element(By.XPATH, '//*[@id="prod-review-nav-link"]/span[1]/span').get_attribute('style')
            import re
            width = re.search(r"width:\s*(\d+)", starScore)
            if width:
                widthVal = width.group(1)
            else:
                widthVal = None
            widthVal = widthVal.replace('%', '')
            starScore = (float)(int(widthVal, base=0)) / 20
            self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]').click()
            self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[1]/div[3]/span').click()
            starScoreBestRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[2]/div[3]').text
            starScoreBestRate = starScoreBestRate.replace('%', '')
            starScoreBestRate = (float)(int(starScoreBestRate, base=0))/100
            starScoreGoodRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[3]/div[3]').text
            starScoreGoodRate = starScoreGoodRate.replace('%', '')
            starScoreGoodRate = (float)(int(starScoreGoodRate, base=0))/100
            starScoreBadRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[5]/div[3]').text
            starScoreBadRate = starScoreBadRate.replace('%', '')
            starScoreBadRate = (float)(int(starScoreBadRate, base=0))/100
            starScoreWorstRate = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[6]/div[3]').text
            starScoreWorstRate = starScoreWorstRate.replace('%', '')
            starScoreWorstRate = (float)(int(starScoreWorstRate, base=0))/100
            reviewCount = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]/span').text
            reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
            reviewCount = (int)(reviewCount, base=0)
            buyCount = 0
            saleCompany = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/a').text
            deliveryPrice = self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[7]/div[3]/div[1]/div[1]/div[1]/span/em[1]').text
            if (deliveryPrice == '무료배송'):
                deliveryPrice = 0
            collect = '수집완료'
            brandName = saleCompany
            category = self.driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[2]/a').text
            venderItemId = '알 수 없음'
            dealProjectName = event
            dealNo = i
            storeFriend = '알 수 없음'
            likeCount = 0
            priceUnit = 0
            division = self.driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[3]/a').text
            created = datetime.now()
            updated = datetime.now()
            updater = 'root'
            collection_date = datetime.now()
            commerceType = 'COUPANG'
            discountProvider = 0
            discountPriceCommerce = 0
            etcDeliveryName = ''
            searchWord = '행사'
            adsYn = 'Y'
            url = productUrl
            creator = 0

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[-1])
            data = {
                'product_no': productNo,
                'product_name':productName,
                'list_price': listPrice,
                'price':price,
                'discount_rate':discountRate,
                'discount_price': discountPrice,
                'discount_rate_commerce':discountRateCommerce,
                'discount_coupon_name':discountCouponName,
                'discount_double':discountDouble,
                'discount_rate_double':discountRateDouble,
                'discount_coupon_name_double':discountCouponNameDouble,
                'total_price':totalPrice,
                'best_rank':bestRank,
                'star_score':starScore,
                'star_score_best_rate':starScoreBestRate,
                'star_score_good_rate':starScoreGoodRate,
                'star_score_bad_rate':starScoreBadRate,
                'star_score_worst_rate':starScoreWorstRate,
                'review_count':reviewCount,
                'buy_count':buyCount,
                'sale_company':saleCompany,
                'delivery_price':deliveryPrice,
                'product_url':productUrl,
                'product_option':productOption,
                'delivery_type':deliveryType,
                'collect':collect,
                'brand_name':brandName,
                'category':category,
                'vendor_item_id':venderItemId,
                'event':event,
                'deal_project_name':dealProjectName,
                'deal_no':dealNo,
                'store_friend':storeFriend,
                'like_count':likeCount,
                'price_unit':priceUnit,
                'division':division,
                'created':created,
                'updated':updated,
                'updater':updater,
                'collection_date':collection_date,
                'commerce_type':commerceType,
                'discount_provider':discountProvider,
                'discount_price_commerce':discountPriceCommerce,
                'etc_delivery_name':etcDeliveryName,
                'search_word':searchWord,
                'ads_yn':adsYn,
                'url':url,
                'creator':creator
            }

            self.driver.back()
            i += 1
            dbInfo.insert_data(self.dbconn, self.cursor, data)


    def total_category(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('coupang_category.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("coupang_category.html", "w")
            f.write(soup.prettify())
            f.close()
        
        #정보 크롤링
        productCategory = self.driver.find_element(By.XPATH, '//*[@id="searchOptionForm"]/div/div/div[1]/div/div[1]/h3').text
        ul = self.driver.find_element(By.XPATH, '//*[@id="productList"]')
        lis = ul.find_elements(By.XPATH, './/li')
        i = 1
        for li in lis:
            data = {}
            id = li.get_attribute("id")
            productNo = id
            try: 
                adsYn = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/span/span[1]')
                adsYn = 'Y'
            except NoSuchElementException:
                adsYn = 'N'
            productName = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div[2]').text
            try:
                listPrice = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div[3]/div/div[1]/span[1]/del').text
                listPrice = listPrice.replace(',', '')
                listPrice = (int)(listPrice, base=0)
            except NoSuchElementException:
                listPrice = 0

            try:
                price = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div[3]/div/div[1]/em/strong').text
                price = price.replace(',', '')
                price = (int)(price, base=0)
            except NoSuchElementException:
                price = 0
            
            discountProvider = 0
            discountPriceCommerce = 0
            discountCouponName = 'sale'
            discountDouble = 0
            try:
                discountRateDouble = self.driver.find_element(By.CLASS_NAME, 'instant-discount-rate').text
                discountRateDouble = discountRateDouble.replace('%', '')
                discountRateDouble = int(discountRateDouble, base=0)
            except NoSuchElementException:
                discountRateDouble = 0
            discountCouponNameDouble = '알 수 없음'
            totalPrice = price
            bestRank = -1
            try:
                starScore = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div[4]/div/span[1]/em').text
                starScore = (float)(starScore)
            except NoSuchElementException:
                starScore = 0
            try:
                reviewCount = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[4]/div/span[2]').text
                reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                reviewCount = (int)(reviewCount, base=0)
            except:
                reviewCount = 0
            buyCount = 0
            saleCompany = 'COUPANG'
            deliveryPrice = 0
            productUrl = self.driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a').get_attribute('href')
            deliveryType = "로켓배송"
            searchWord = '즉석밥'
            adArea = '상품리스트'
            optionName = '알 수 없음'
            likeClick = 0
            salesMan = 'COUPANG'
            optionNo = 0
            brandName = '알 수 없음'
            event = '없음'
            vendorItemId = li.get_attribute("data-vendor-item-id")
            collectionDate = datetime.now()
            commerceType = 'COUPANG'
            created = datetime.now()
            updated = datetime.now()
            updater = 1
            etcDeliveryName = '알 수 없음'
            referenceId = 0
            dataRanking = i
            creator = 1

            data = {
                'product_name': productName,
                'product_no':productNo,
                'list_price': listPrice,
                'price':price,
                'discount_provider':discountProvider,
                'discount_price_commerce': discountPriceCommerce,
                'discount_coupon_name':discountCouponName,
                'discount_double':discountDouble,
                'discount_rate_double':discountRateDouble,
                'discount_coupon_name_double':discountCouponNameDouble,
                'total_price':totalPrice,
                'best_rank':bestRank,
                'star_score':starScore,
                'review_count':reviewCount,
                'buy_count':buyCount,
                'sale_company':saleCompany,
                'delivery_price':deliveryPrice,
                'product_url':productUrl,
                'delivery_type':deliveryType,
                'search_word':searchWord,
                'ad_area':adArea,
                'option_name':optionName,
                'like_click':likeClick,
                'salesman':salesMan,
                'option_no':optionNo,
                'brand_name':brandName,
                'event':event,
                'vendor_item_id':vendorItemId,
                'collection_date':collectionDate,
                'commerce_type':commerceType,
                'created':created,
                'updated':updated,
                'updater':updater,
                'etc_delivery_name':etcDeliveryName,
                'reference_id':referenceId,
                'product_category':productCategory,
                'ads_yn':adsYn,
                'data_ranking':dataRanking,
                'creator':creator
            }

            i += 1
            dbInfo.insert_data(self.dbconn, self.cursor, data)


    def total_review(self):
        self.driver.get(self.url)
        self.driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('coupang_review.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("coupang_review.html", "w")
            f.write(soup.prettify())
            f.close()

        #정보 크롤링
        self.driver.find_element(By.CSS_SELECTOR, '.count').click()
        self.driver.implicitly_wait(5)

        articles = self.driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[6]/section[4]')
        article = articles.find_elements(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[6]/section[4]/article')

        for ar in article:
            productName = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__info__product-info__name').text
            userName = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__info__user__name').text
            rating = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__info__product-info__star-orange')
            if rating == None:
                rating = 0
            else :
                rating = int(rating.get_attribute('data-rating'))
            headline = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__headline').text
            reviewContent = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__review > div').text
            try:
                liked = ar.find_element(By.CSS_SELECTOR, '.sdp-review__article__list__survey__row__answer').text
            except NoSuchElementException:
                liked = '평가 없음'
            data = {
                'product_name':productName,
                'user_name':userName,
                'rating':rating,
                'headline':headline,
                'review_content':reviewContent,
                'liked':liked
            }

            dbInfo.insert_data(self.dbconn, self.cursor, data)
