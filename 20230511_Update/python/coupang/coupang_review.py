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
            INSERT IGNORE INTO tb_total_review
            (
                PRODUCT_NAME, USER_NAME, RATING, HEADLINE, REVIEW_CONTENT, LIKED
            ) 
            VALUES (
                "{data['product_name']}", "{data['user_name']}", "{data['rating']}", "{data['headline']}", "{data['review_content']}", "{data['liked']}"
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

    def total_review(self):
        url = 'https://www.coupang.com/vp/products/6135394118?itemId=13195279382&vendorItemId=81917799353&q=즉석밥&itemsCount=36&searchId=c0b0d5eada62494186142bf02cd63393&rank=0&isAddedCart='
        driver.get(url=url)
        time.sleep(5)

        # html 정보 출력
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        f = open("coupang_review.html", "w")
        f.write(soup.prettify())
        f.close()

        driver.find_element(By.CSS_SELECTOR, '.count').click()
        time.sleep(5)

        articles = driver.find_element(By.XPATH, '//*[@id="btfTab"]/ul[2]/li[3]/div/div[6]/section[4]')
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
GetTotalReview = GetData.total_review()

dbconn.close()
driver.quit()