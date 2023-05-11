from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import subprocess
import time 
import mysql.connector
import re
from urllib.request import urlopen
from datetime import datetime

# 특수문자 제거
def remove_sc(sentence) : 
    return re.sub('[-=.#/?:$}\"\']', '', str(sentence)).replace('[','').replace(']','')

# 웹사이트 인코딩 방식 확인
def get_encoding(url) : 
    f = urlopen(url)    
    # bytes자료형의 응답 본문을 일단 변수에 저장
    bytes_content = f.read()
    
    # charset은 HTML의 앞부분에 적혀 있는 경우가 많으므로
    # 응답 본문의 앞부분 1024바이트를 ASCII문자로 디코딩 해둔다.
    # ASCII 범위 이외에 문자는 U+FFFD(REPLACEMENT CHARACTRE)로 변환되어 예외가 발생하지 않는다.
    scanned_text = bytes_content[:1024].decode('ascii', errors='replace')
    
    # 디코딩한 문자열에서 정규 표현식으로 charset값 추출
    # charset이 명시돼 있지 않으면 UTF-8 사용
    match = re.search(r'charset=["\']?([\w-]+)', scanned_text)
    if match : 
        encoding = match.group(1)
    else :   
        encoding = 'utf-8'
        
    return encoding

# DB Insert
def insert_data(dbconn, cursor, data) : 
    try : 
        cursor.execute(f"""
            INSERT IGNORE INTO tb_total_price
            (
                PRODUCT_NO, PRODUCT_NAME, LIST_PRICE, PRICE, DISCOUNT_RATE, 
                DISCOUNT_PRICE, DISCOUNT_RATE_COMMERCE, DISCOUNT_COUPON_NAME, DISCOUNT_DOUBLE, DISCOUNT_RATE_DOUBLE,
                DISCOUNT_COUPON_NAME_DOUBLE, TOTAL_PRICE, BEST_RANK, STAR_SCORE, STAR_SCORE_BEST_RATE, 
                STAR_SCORE_GOOD_RATE, STAR_SCORE_BAD_RATE, STAR_SCORE_WORST_RATE, REVIEW_COUNT, BUY_COUNT, 
                SALE_COMPANY, DELIVERY_PRICE, PRODUCT_URL, PRODUCT_OPTION, DELIVERY_TYPE,
                COLLECT, BRAND_NAME, CATEGORY, VENDOR_ITEM_ID, EVENT, 
                DEAL_PROJECT_NAME, DEAL_NO, STORE_FRIEND, LIKE_COUNT, PRICE_UNIT, 
                DIVISION, CREATED, UPDATED, UPDATER, COLLECTION_DATE, 
                COMMERCE_TYPE, DISCOUNT_PROVIDER, DISCOUNT_PRICE_COMMERCE, ETC_DELIVERY_NAME, SEARCH_WORD, 
                ADS_YN, URL, CREATOR
            ) 
            VALUES (
                "{data['product_no']}", "{data['product_name']}", "{data['list_price']}", "{data['price']}", "{data['discount_rate']}", 
                "{data['discount_price']}", "{data['discount_rate_commerce']}", "{data['discount_coupon_name']}", "{data['discount_double']}", "{data['discount_rate_double']}", 
                "{data['discount_coupon_name_double']}", "{data['total_price']}", "{data['best_rank']}", "{data['star_score']}", "{data['star_score_best_rate']}", 
                "{data['star_score_good_rate']}", "{data['star_score_bad_rate']}", "{data['star_score_worst_rate']}", "{data['review_count']}", "{data['buy_count']}", 
                "{data['sale_company']}", "{data['delivery_price']}", "{data['product_url']}", "{data['product_option']}", "{data['delivery_type']}", 
                "{data['collect']}", "{data['brand_name']}", "{data['category']}", "{data['vendor_item_id']}", "{data['event']}", 
                "{data['deal_project_name']}", "{data['deal_no']}", "{data['store_friend']}", "{data['like_count']}", "{data['price_unit']}", 
                "{data['division']}", "{data['created']}", "{data['updated']}", "{data['updater']}", "{data['collection_date']}", 
                "{data['commerce_type']}", "{data['discount_provider']}", "{data['discount_price_commerce']}", "{data['etc_delivery_name']}", "{data['search_word']}", 
                "{data['ads_yn']}", "{data['url']}", "{data['creator']}"
            ) 
        """)
    except Exception as e :
        print(f'***** + insert_data error! >> {e}')
    finally : 
        dbconn.commit()
        print('****  상품 insert 완료! ')

class GetData :
    def __init__(self, dbconn, cursor) : 
        self.dbconn = dbconn
        self.cursor = cursor

    def total_price(self):
        url = 'https://www.coupang.com/np/search?q=top100&channel=relate'
        driver.get(url=url)
        time.sleep(5)

        # html 정보 출력
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        f = open("coupang_price.html", "w")
        f.write(soup.prettify())
        f.close()

        list = driver.find_element(By.XPATH, '//*[@id="productList"]')
        lis = list.find_elements(By.XPATH, './/li')

        i = 1
        for li in lis:
            data = {}
            productUrl = driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').get_attribute('href')

            productName = driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[2]').text
            deliveryType = driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[3]/div/div[3]/span').text
            discountCouponName = '없음'
            totalPrice = driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
            totalPrice = totalPrice.replace(',', '')
            totalPrice = (int)(totalPrice, base=0)
            productOption = '없음'
            event = '없음'
            driver.find_element(By.XPATH, '//*[@id="productList"]/li[' + str(i) + ']/a').click()
            time.sleep(5)

            driver.switch_to.window(driver.window_handles[-1]) 
            try:
                listPrice = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[2]/span[1]/strong').text
                listPrice = listPrice.replace(',', '').replace('원', '')
                listPrice = (int)(listPrice, base=0)
            except NoSuchElementException:
                listPrice = 0
            productNo = driver.find_element(By.XPATH, '//*[@id="contents"]').get_attribute("data-product-id")
            try:
                price = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[3]/span[1]/strong').text
                price = price.replace(',', '').replace('원', '')
                price = (int)(price, base=0)
            except NoSuchElementException:
                price = 0
        
            discountRate = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRate = discountRate.replace('%', '')
            discountRate = (float)(int(discountRate, base=0))/100
            discountPrice = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[2]').text
            discountRateCommerce = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[5]/div[1]/div/div[1]/span[1]').text
            discountRateCommerce = discountRateCommerce.replace('%', '')
            discountRateCommerce = float(int(discountRateCommerce, base=0))/100
            discountCouponName = '쿠폰'
            discountDouble = '알 수 없음'
            discountRateDouble = '알 수 없음'
            discountCouponNameDouble = '알 수 없음'
            bestRank = -1
            starScore = driver.find_element(By.XPATH, '//*[@id="prod-review-nav-link"]/span[1]/span').get_attribute('style')
            width = re.search(r"width:\s*(\d+)", starScore)
            if width:
                widthVal = width.group(1)
            else:
                widthVal = None
            widthVal = widthVal.replace('%', '')
            widthVal = (float)(int(widthVal, base=0)) / 20
            driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]').click()
            driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[1]/div[3]/span').click()
            starScoreBestRate = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[2]/div[3]').text
            starScoreBestRate = starScoreBestRate.replace('%', '')
            starScoreBestRate = (float)(int(starScoreBestRate, base=0))/100
            starScoreGoodRate = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[3]/div[3]').text
            starScoreGoodRate = starScoreGoodRate.replace('%', '')
            starScoreGoodRate = (float)(int(starScoreGoodRate, base=0))/100
            starScoreBadRate = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[5]/div[3]').text
            starScoreBadRate = starScoreBadRate.replace('%', '')
            starScoreBadRate = (float)(int(starScoreBadRate, base=0))/100
            starScoreWorstRate = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[4]/section[1]/div[2]/div[2]/div[6]/div[3]').text
            starScoreWorstRate = starScoreWorstRate.replace('%', '')
            starScoreWorstRate = (float)(int(starScoreWorstRate, base=0))/100
            reviewCount = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[1]/li[2]/span').text
            reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
            reviewCount = (int)(reviewCount, base=0)
            buyCount = 0
            saleCompany = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/a').text
            try:
                deliveryPrice = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div[3]/div[7]/div[3]/div[1]/div[1]/div[1]/span/em[1]').text
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
            category = driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[2]/a').text
            venderItemId = '알 수 없음'
            dealProjectName = event
            dealNo = i
            storeFriend = '알 수 없음'
            likeCount = 0
            priceUnit = 0
            division = driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/li[3]/a').text
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

            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
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
            insert_data(self.dbconn, self.cursor, data)

#연결
subprocess.Popen(f'google-chrome --remote-debugging-port=9222  --user-data-dir=data_dir'.split()) 
chrome_option = Options()
#chrome_option.add_argument('headless')
chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
try:
 driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
except:
 chromedriver_autoinstaller.install(True)
 driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=chrome_option)
driver.implicitly_wait(10)

#login
driver.get('https://login.coupang.com/login/login.pang')
time.sleep(5)

id_input = driver.find_element(By.XPATH, '//*[@id="login-email-input"]')
id_input.send_keys('**id**')

pw_input = driver.find_element(By.XPATH, '//*[@id="login-password-input"]')
pw_input.send_keys('**pwd**')

driver.find_element(By.XPATH, '/html/body/div[1]/div/div/form/div[5]/button').click()
time.sleep(5)

dbconn = mysql.connector.connect(host='127.0.0.1', user='root', password='1234', db='coupangdb', port='3306')
cursor = dbconn.cursor(buffered=True)

GetData = GetData(dbconn, cursor)
GetTotalPrice = GetData.total_price()

dbconn.close()
driver.quit()