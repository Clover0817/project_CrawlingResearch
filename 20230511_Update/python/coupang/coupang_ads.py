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
            INSERT IGNORE INTO tb_total_ads
            (
                PRODUCT_NAME, PRODUCT_NO, LIST_PRICE, PRICE, 
                DISCOUNT_PROVIDER, DISCOUNT_PRICE_COMMERCE, DISCOUNT_COUPON_NAME, DISCOUNT_DOUBLE, DISCOUNT_RATE_DOUBLE,
                DISCOUNT_COUPON_NAME_DOUBLE, TOTAL_PRICE, BEST_RANK, STAR_SCORE, REVIEW_COUNT, 
                BUY_COUNT, SALE_COMPANY, DELIVERY_PRICE, PRODUCT_URL, DELIVERY_TYPE, 
                SEARCH_WORD, AD_AREA, OPTION_NAME, LIKE_CLICK, SALESMAN, 
                OPTION_NO, BRAND_NAME, EVENT, VENDOR_ITEM_ID, COLLECTION_DATE, 
                COMMERCE_TYPE, CREATED, UPDATED, UPDATER, ETC_DELIVERY_NAME,
                REFERENCE_ID, PRODUCT_CATEGORY, ADS_YN, DATA_RANKING, CREATOR
            ) 
            VALUES (
                "{data['product_name']}", "{data['product_no']}", "{data['list_price']}", "{data['price']}", 
                "{data['discount_provider']}", "{data['discount_price_commerce']}", "{data['discount_coupon_name']}", "{data['discount_double']}", "{data['discount_rate_double']}", 
                "{data['discount_coupon_name_double']}", "{data['total_price']}", "{data['best_rank']}", "{data['star_score']}", "{data['review_count']}", 
                "{data['buy_count']}", "{data['sale_company']}", "{data['delivery_price']}", "{data['product_url']}", "{data['delivery_type']}", 
                "{data['search_word']}", "{data['ad_area']}", "{data['option_name']}", "{data['like_click']}", "{data['salesman']}", 
                "{data['option_no']}", "{data['brand_name']}", "{data['event']}", "{data['vendor_item_id']}", "{data['collection_date']}", 
                "{data['commerce_type']}", "{data['created']}", "{data['updated']}", "{data['updater']}", "{data['etc_delivery_name']}", 
                "{data['reference_id']}", "{data['product_category']}", "{data['ads_yn']}", "{data['data_ranking']}", "{data['creator']}"
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

    def total_ads(self):
        url = "https://www.coupang.com/np/search?component=&q=즉석밥&channel=user"
        driver.get(url=url)
        time.sleep(5)

        # html 정보 출력
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        f = open("coupang_ads.html", "w")
        f.write(soup.prettify())
        f.close()

        ul = driver.find_element(By.XPATH, '//*[@id="productList"]')
        lis = ul.find_elements(By.XPATH, './/li')
        i = 1
        for li in lis:
            data = {}
            try: 
                id = li.get_attribute("id")
                productNo = id
                adsYn = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/span/span[1]')
                adsYn = 'Y'

                productName = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[2]').text
                try:
                    listPrice = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/span[1]/del').text
                    listPrice = listPrice.replace(',', '')
                    listPrice = (int)(listPrice, base=0)
                except NoSuchElementException:
                    listPrice = 0

                price = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
                try:
                    price = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[3]/div/div[1]/em/strong').text
                    price = price.replace(',', '')
                    price = (int)(price, base=0)
                except NoSuchElementException:
                    price = 0
                
                discountProvider = 0
                discountPriceCommerce = 0
                discountCouponName = 'sale'
                discountDouble = 0
                discountRateDouble = driver.find_element(By.CLASS_NAME, 'instant-discount-rate').text
                discountRateDouble = discountRateDouble.replace('%', '')
                discountRateDouble = int(discountRateDouble, base=0)
                discountCouponNameDouble = '알 수 없음'
                totalPrice = price
                bestRank = -1
                try:
                    starScore = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[4]/div/span[1]/em').text
                    starScore = (float)(starScore)
                except NoSuchElementException:
                    starScore = 0
                reviewCount = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a/dl/dd/div/div[4]/div/span[2]').text
                reviewCount = reviewCount.replace('(', '').replace(',', '').replace(')', '')
                reviewCount = (int)(reviewCount, base=0)
                buyCount = 0
                saleCompany = 'COUPANG'
                deliveryPrice = 0
                productUrl = driver.find_element(By.XPATH, '//*[@id="' + id + '"]/a').get_attribute('href')
                deliveryType = "로켓배송"
                searchWord = driver.find_element(By.XPATH, '//*[@id="searchOptionForm"]/input[3]').get_attribute('value')
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
                productCategory = driver.find_element(By.XPATH, '//*[@id="searchCategoryComponent"]/ul/li[1]/label').text
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
                insert_data(self.dbconn, self.cursor, data)
            except NoSuchElementException:
                continue

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
GetTotalAds = GetData.total_ads()

dbconn.close()
driver.quit()