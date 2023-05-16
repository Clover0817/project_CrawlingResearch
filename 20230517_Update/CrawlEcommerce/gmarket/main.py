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

#driver 연결
subprocess.Popen(f'google-chrome --remote-debugging-port=9222  --user-data-dir=data_dir'.split()) 
chrome_option = Options()
chrome_option.add_argument('headless')
chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
try:
    driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
except:
    chromedriver_autoinstaller.install(True)

driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
driver.implicitly_wait(10)

class Gmarket:
    def __init__(self, url, login_mode): 
        #초기화
        self.url = url
        self.login_mode = login_mode

        #DB 연결
        dbconn = mysql.connector.connect(host=dbInfo.host, user=dbInfo.user, password=dbInfo.password, db=dbInfo.gmarket_db, port=dbInfo.port)
        cursor = dbconn.cursor(buffered=True)
        self.GmarketData = GmarketData(self.url, dbconn, cursor)
        
        #로그인 여부
        if self.login_mode == 1:
            GmarketData.login()

    def search(self):
        self.GmarketData.total_ads()
        self.dbconn.close()
        driver.quit()
 
    def best(self):
        self.GmarketData.total_best()
        self.dbconn.close()
        driver.quit()
        
    def event(self):
        self.GmarketData.total_event()
        self.dbconn.close() 
        driver.quit()

    def category(self):
        self.GmarketData.total_categoty()
        self.dbconn.close()
        driver.quit()

    def review(self):
        self.GmarketData.total_review()
        self.dbconn.close()
        driver.quit()
          

class GmarketData:
    def __init__(self, url, dbconn, cursor) : 
          #초기화
          self.url = url
          self.dbconn = dbconn
          self.cursor = cursor

    
    def login():
          driver.get('https://signinssl.gmarket.co.kr/login/login?url=https://www.gmarket.co.kr/')

          user_id = driver.find_element(By.XPATH, '//*[@id="typeMemberInputId"]')
          user_id.send_keys(loginInfo.gmarket_id)
          user_pw = driver.find_element(By.XPATH, '//*[@id="typeMemberInputPassword"]')
          user_pw.send_keys(loginInfo.gmarket_password)

          driver.find_element(By.XPATH, '//*[@id="btn_memberLogin"]').click()
          driver.implicitly_wait(5)
        
    def total_ads(self):
        driver.get(self.url)
        driver.implicitly_wait(10)

        #html 정보 출력
        if os.path.isfile('gmarket_ads.html'):
            print("파일이 존재합니다.")
        else:
            from bs4 import BeautifulSoup
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            f = open("gmarket_ads.html", "w")
            f.write(soup.prettify())
            f.close()

        ul = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div/ul')
        lis = ul.find_elements(By.XPATH, './/li')
        i = 1
        for li in lis:
            data = {}
            adsYn = 'Y'
            productUrl = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div/ul/li[' + str(i) + ']/div/div[1]/a').get_attribute('href')
            driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div/ul/li[' + str(i) + ']').click()
            driver.implicitly_wait(5)

            driver.switch_to.window(driver.window_handles[-1]) 
            driver.find_element(By.XPATH, '/html/body/div[3]/div/span').text
            productName = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/h1').text
            productNo = driver.find_element(By.XPATH, '/html/body/div[3]/div/span').text
            productNo = productNo[8:]
            productNo = (int)(productNo.lstrip('0'), base=0)
            try:
                listPrice = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[5]/span[2]/strong').text
                listPrice = listPrice.replace(',', '').replace('원', '')
                listPrice = (int)(listPrice, base=0)
            except NoSuchElementException:
                listPrice = 0
            try:
                price = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[5]/span[3]/strong').text
                price = price.replace(',', '').replace('원', '')
                price = (int)(price, base=0)
            except NoSuchElementException:
                price = 0
                
            discountProvider = 0
            discountPriceCommerce = 0
            discountCouponName = 'sale'
            discountDouble = 0
            discountRateDouble = (float(listPrice-price)/listPrice)*100
            try:
                discountCouponNameDouble = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[5]/span[3]/div/ul/li[2]/em').text
            except NoSuchElementException:
                discountCouponNameDouble = '알 수 없음'
            totalPrice = price
            bestRank = -1
            starScore = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/div/span').get_attribute('style')
            import re
            width = re.search(r"width:\s*(\d+)", starScore)
            if width:
                widthVal = width.group(1)
            else:
                widthVal = None
            widthVal = widthVal.replace('%', '')
            starScore = (float)(int(widthVal, base=0)) / 20
            reviewCount = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/span[2]').text
            reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
            reviewCount = (int)(reviewCount, base=0)
            buyCount = 0
            saleCompany = 'GMARKET'
            deliveryPrice = 0
            try:
                deliveryType = driver.find_element(By.XPATH, '//*[@id="container"]/div[3]/div[2]/div[2]/ul/li[4]/div/div').text
            except NoSuchElementException:
                deliveryType = "일반배송"

            searchWord = driver.find_element(By.XPATH, '//*[@id="skip-navigation-search"]/span/button').get_attribute('data-montelena-keyword')
            adArea = '상품리스트'
            optionName = '알 수 없음'
            likeClick = 0
            salesMan = 'GMARKET'
            optionNo = 0
            brandName = '알 수 없음'
            event = '없음'
            vendorItemId = productNo
            collectionDate = datetime.now()
            commerceType = 'GMARKET'
            created = datetime.now()
            updated = datetime.now()
            updater = 1
            etcDeliveryName = '알 수 없음'
            referenceId = 0
            productCategory = driver.find_element(By.XPATH, '/html/body/div[3]/ul/li[2]/a').text
            dataRanking = i
            creator = 1

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
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
        
        #자원 정리
        driver.quit()


    def total_best(self):
          driver.get(self.url)
          driver.implicitly_wait(10)

          #html 정보 출력
          if os.path.isfile('gmarket_ads.html'):
               print("파일이 존재합니다.")
          else:
               from bs4 import BeautifulSoup
               html = driver.page_source
               soup = BeautifulSoup(html, 'html.parser')
               f = open("gmarket_ads.html", "w")
               f.write(soup.prettify())
               f.close()
          ul = driver.find_elements(By.XPATH, '//*[@id="gBestWrap"]/div[2]/ul/li')
          i = 1
          for li in ul:
               data = {}
               productUrl = driver.find_element(By.XPATH, '//*[@id="gBestWrap"]/div[2]/ul/li[' + str(i) + ']/div[1]/a').get_attribute('href')

               driver.find_element(By.XPATH, '//*[@id="gBestWrap"]/div[2]/ul/li[' + str(i) + ']/div[1]/a').click()
               driver.implicitly_wait(5)

               productName = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/h1').text
               try:
                    deliveryType = driver.find_element(By.XPATH, '//*[@id="ship_open"]/div/div[1]/span[2]').text
               except NoSuchElementException:
                    deliveryType = '일반 배송'
               try:
                    discountCouponName = driver.find_element(By.XPATH, '//*[@id="vip_coupon_optimal_banner"]/button/span[1]/span').text
               except NoSuchElementException:
                    discountCouponName = '없음'
               try:
                    totalPrice = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[4]/span[2]/strong').text
                    totalPrice = totalPrice.replace(',', '').replace('원', '')
                    totalPrice = (int)(totalPrice, base=0)
               except NoSuchElementException:
                    totalPrice = 0
               productOption = '없음'
               event = '알 수 없음'
               
               try:
                    listPrice = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[4]/span[2]/span/span[1]').text
                    listPrice = listPrice.replace(',', '').replace('원', '')
                    listPrice = (int)(listPrice, base=0)
               except NoSuchElementException:
                    listPrice = 0
               productNo = str(i)
               try:
                    price = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[4]/span[3]/strong').text
                    price = price.replace(',', '').replace('원', '')
                    price = (int)(price, base=0)
               except NoSuchElementException:
                    price = 0
          
               if listPrice > price:
                    discountRate = (float(listPrice-price)/listPrice)*100
                    discountPrice = listPrice - price
               else:
                    discountRate = 0
                    discountPrice = 0
               discountRateCommerce = discountRate
               discountCouponName = '알 수 없음'
               discountDouble = '알 수 없음'
               discountRateDouble = '알 수 없음'
               discountCouponNameDouble = '알 수 없음'
               bestRank = -1
               try:
                    starScore = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/div/span').get_attribute('style')
                    import re
                    width = re.search(r"width:\s*(\d+)", starScore)
                    if width:
                         widthVal = width.group(1)
                    else:
                         widthVal = None
                         widthVal = widthVal.replace('%', '')
                         starScore = (float)(int(widthVal, base=0)) / 20
               except NoSuchElementException:
                    starScore = 0
                    starScoreBestRate = 0
                    starScoreGoodRate = 0
                    starScoreBadRate = 0
                    starScoreWorstRate = 0
               try:
                    reviewCount = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/span[2]').text
                    reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                    reviewCount = (int)(reviewCount, base=0)
               except NoSuchElementException:
                    reviewCount = 0
               buyCount = 0
               saleCompany = 'GMARKET'
               deliveryPrice = 0
               collect = '수집완료'
               brandName = saleCompany
               category = '알 수 없음'
               venderItemId = '알 수 없음'
               dealProjectName = event
               dealNo = i
               storeFriend = '알 수 없음'
               likeCount = 0
               priceUnit = 0
               division = category
               created = datetime.now()
               updated = datetime.now()
               updater = 'root'
               collection_date = datetime.now()
               commerceType = 'GMARKET'
               discountProvider = 0
               discountPriceCommerce = 0
               etcDeliveryName = ''
               searchWord = '행사'
               adsYn = 'Y'
               url = productUrl
               creator = 0

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

               driver.back()
               i += 1
               dbInfo.insert_data(self.dbconn, self.cursor, data)
          #자원 정리
          driver.quit()

    def total_event(self):
          driver.get(self.url)
          driver.implicitly_wait(10)

          #html 정보 출력
          if os.path.isfile('gmarket_event.html'):
               print("파일이 존재합니다.")
          else:
               from bs4 import BeautifulSoup
               html = driver.page_source
               soup = BeautifulSoup(html, 'html.parser')
               f = open("gmarket_event.html", "w")
               f.write(soup.prettify())
               f.close() 
          ul = driver.find_elements(By.XPATH, '//*[@id="container"]/div[2]/ul/li')

          #정보 크롤링
          i = 1
          for li in ul:
               data = {}
               productUrl = driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/ul/li[' + str(i) + ']/div/a').get_attribute('href')

               driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/ul/li[' + str(i) + ']/div/a').click()
               driver.implicitly_wait(5)

               productName = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/h1').text
               try:
                    deliveryType = driver.find_element(By.XPATH, '//*[@id="ship_open"]/div/div[1]/span[2]').text
               except NoSuchElementException:
                    deliveryType = '일반 배송'
               try:
                    discountCouponName = driver.find_element(By.XPATH, '//*[@id="vip_coupon_optimal_banner"]/button/span[1]/span').text
               except NoSuchElementException:
                    discountCouponName = '없음'
               try:
                    totalPrice = driver.find_element(By.XPATH, '//*[@id="goodsDetailTab"]/div[3]/div/div[5]/div[1]/span/span/span[2]').text
                    totalPrice = totalPrice.replace(',', '')
                    totalPrice = (int)(totalPrice, base=0)
               except NoSuchElementException:
                    totalPrice = 0
               productOption = '없음'
               event = '알 수 없음'
               
               try:
                    listPrice = driver.find_element(By.XPATH, '//*[@id="goodsDetailTab"]/div[3]/div/div[5]/div[1]/del/span[2]').text
                    listPrice = listPrice.replace(',', '')
                    listPrice = (int)(listPrice, base=0)
               except NoSuchElementException:
                    listPrice = 0
               productNo = str(i)
               try:
                    price = driver.find_element(By.XPATH, '//*[@id="goodsDetailTab"]/div[3]/div/div[5]/div[1]/span/span/span[2]').text
                    price = price.replace(',', '')
                    price = (int)(price, base=0)
               except NoSuchElementException:
                    price = 0
          
               if listPrice > price:
                    discountRate = (float(listPrice-price)/listPrice)*100
                    discountPrice = listPrice - price
               else:
                    discountRate = 0
                    discountPrice = 0
               discountRateCommerce = discountRate
               discountCouponName = '알 수 없음'
               discountDouble = '알 수 없음'
               discountRateDouble = '알 수 없음'
               discountCouponNameDouble = '알 수 없음'
               bestRank = -1
               try:
                    starScore = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/div/span').get_attribute('style')
                    import re
                    width = re.search(r"width:\s*(\d+)", starScore)
                    if width:
                         widthVal = width.group(1)
                    else:
                         widthVal = None
                         widthVal = widthVal.replace('%', '')
                         starScore = (float)(int(widthVal, base=0)) / 20
               except NoSuchElementException:
                    starScore = 0
                    starScoreBestRate = 0
                    starScoreGoodRate = 0
                    starScoreBadRate = 0
                    starScoreWorstRate = 0
               try:
                    reviewCount = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/div[2]/span[2]').text
                    reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                    reviewCount = (int)(reviewCount, base=0)
               except NoSuchElementException:
                    reviewCount = 0
               buyCount = 0
               saleCompany = 'GMARKET'
               deliveryPrice = 0
               collect = '수집완료'
               brandName = saleCompany
               category = '알 수 없음'
               venderItemId = '알 수 없음'
               dealProjectName = event
               dealNo = i
               storeFriend = '알 수 없음'
               likeCount = 0
               priceUnit = 0
               division = category
               created = datetime.now()
               updated = datetime.now()
               updater = 'root'
               collection_date = datetime.now()
               commerceType = 'GMARKET'
               discountProvider = 0
               discountPriceCommerce = 0
               etcDeliveryName = ''
               searchWord = '행사'
               adsYn = 'Y'
               url = productUrl
               creator = 0

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

               driver.back()
               i += 1
               dbInfo.insert_data(self.dbconn, self.cursor, data)
          #자원 정리
          driver.quit()

    def total_category(self):
          driver.get(self.url)
          driver.implicitly_wait(10)

          #html 정보 출력
          if os.path.isfile('gmarket_category.html'):
               print("파일이 존재합니다.")
          else:
               from bs4 import BeautifulSoup
               html = driver.page_source
               soup = BeautifulSoup(html, 'html.parser')
               f = open("gmarket_category.html", "w")
               f.write(soup.prettify())
               f.close() 

          #정보 크롤링
          productCategory = driver.find_element(By.XPATH, '//*[@id="box__toggle-filter-c"]/div/ul/li/a/span').text
          divs = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]')
          div = driver.find_elements(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div')
          i = 1
          for di in div:
               data = {}
               productNo = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[1]/a').get_attribute("data-montelena-goodscode")
               productUrl = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[1]/a').get_attribute('href')

               adsYn = 'N'
               productName = di.find_element(By.CLASS_NAME, 'text__item').text
               try:
                    listPrice = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[1]/div[2]/div[3]/span[2]').text
                    listPrice = listPrice.replace(',', '').replace('원', '')
               except NoSuchElementException:
                    listPrice = 0
               try:
                    price = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[1]/div[2]/div[1]/strong').text
                    price = price.replace(',', '')
                    price = (int)(price, base=0)
               except NoSuchElementException:
                    price = 0
               
               discountProvider = 0
               discountPriceCommerce = 0
               discountCouponName = 'sale'
               discountDouble = 0
               try:
                    discountRateDouble = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[1]/div[2]/div[1]/span[2]').text
                    if (discountRateDouble[-1] == '원'):
                         discountRateDouble = 0
                    else:
                         discountRateDouble = discountRateDouble.replace('%', '')
                         discountRateDouble = float(int(discountRateDouble, base=0))/100
               except NoSuchElementException:
                    discountRateDouble = 0
                    discountCouponNameDouble = '알 수 없음'
                    totalPrice = price
                    bestRank = -1
               try:
                    starScore = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[3]/ul/li[1]/div/span[1]').get_attribute('style')
                    import re
                    width = re.search(r"width:\s*(\d+)", starScore)
                    if width:
                         widthVal = width.group(1)
                    else:
                         widthVal = None
                         widthVal = widthVal.replace('%', '')
                         starScore = (float)(int(widthVal, base=0)) / 20
               except NoSuchElementException:
                    starScore = 0
               try:
                    reviewCount = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[2]/ul/li[2]/span[2]').text
                    reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                    reviewCount = (int)(reviewCount, base=0)
               except NoSuchElementException:
                    reviewCount = 0
               buyCount = 0
               saleCompany = 'GMARKET'
               try:
                    deliveryPrice = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[1]/div[3]/div/ul/li/span').text
                    deliveryPrice = deliveryPrice[4:]
               except NoSuchElementException:
                    deliveryPrice = 0
               try:
                    deliveryType = driver.find_element(By.XPATH, '//*[@id="section__inner-content-body-container"]/div[2]/div[' + str(i) + ']/div[1]/div[2]/div[1]/div[3]/span').text
               except:
                    deliveryType = "일반 배송"
               searchWord = '없음'
               adArea = '상품리스트'
               optionName = '알 수 없음'
               likeClick = 0
               salesMan = 'GMARKET'
               optionNo = 0
               brandName = '알 수 없음'
               event = '없음'
               vendorItemId = productNo
               collectionDate = datetime.now()
               commerceType = 'GMARKET'
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

          #자원 정리
          driver.quit()
     
    def total_review(self):
          productName = driver.find_element(By.XPATH, '//*[@id="itemcase_basic"]/div/h1').text
          driver.find_element(By.XPATH, '//*[@id="container"]/div[6]/div[1]/ul/li[2]/a').click()
          driver.implicitly_wait(5)

          table = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table')
          tr = table.find_elements(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr')

          i = 1
          for t in tr:
               userName = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[3]/dl/dd[1]').text
               recommend = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[1]/span[1]/em').text
               delivery = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[1]/span[2]/em').text
               option = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[2]/p[1]').text
               reviewContent = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[2]/p[2]').text
               date = driver.find_element(By.XPATH, '//*[@id="text-wrapper"]/table/tbody/tr[' + str(i) + ']/td[3]/dl/dd[2]').text

               data = {
                    'product_name':productName,
                    'user_name':userName,
                    'recommend':recommend,
                    'delivery':delivery,
                    'option':option,
                    'review_content':reviewContent,
                    'date':date
               }
               i += 1
               dbInfo.insert_data(self.dbconn, self.cursor, data)
          
          #자원 정리
          driver.quit()
