import os
import sys
from coupang.main import Coupang 
from gmarket.main import Gmarket

site_selection = 0 #0:coupang. 1:gmarket. 2:11st. 3:naver
operation_mode = 0 #0:search. 1:best. 2:event. 3: category. 4:review
searchKeyword = "즉석밥"
url = "https://www.coupang.com/np/search?component=&q=&channel=user"
login_mode = 0 #O:non-login mode. 1: login model

#argv 값은 문자열이므로, int형 변환 필요
if len (sys.argv) >= 2:
    site_selection = int(sys.argv[1])
if len (sys.argv) >= 3:
    operation_selection = int(sys.argv[2])
if len (sys.argv) >= 4:
    url = sys.argv[3]
    #검색 키워드가 들어가는 경우
    if url == "https://www.coupang.com/np/search?component=&q=&channel=user":
        url = url.replace("search?component=&q=", f"search?component=&q={searchKeyword}&channel=user")
if len (sys.argv) >= 5:
    login_mode = int(sys.argv[4])

if site_selection == 0:
    #coupang site
    coupang = Coupang(url, login_mode)
    if operation_mode == 0:
        #search operation
        coupang.search()
        print("1")
    elif operation_mode == 1:
        #best operation
        coupang.best()
    elif operation_mode == 2:
        #event operation
        coupang.event()
    elif operation_mode == 3:
        #category operation
        coupang.category()
    elif operation_mode == 4:
        #review operation
        coupang.review()
    else:
        print("Operation Selection Error")
elif site_selection == 1:
    #gmarket site
    gmarket = Gmarket(url, login_mode)
    if operation_mode == 0:
        #search operation
        gmarket.search()
    elif operation_mode == 1:
        #best operation
        gmarket.best()
    elif operation_mode == 2:
        #event operation
        gmarket.event()
    elif operation_mode == 3:
        #category operation
        gmarket.category()
    elif operation_mode == 4:
        #review operation
        gmarket.review()
    else:
        print("Operation Selection Error")
else:
    print("No Such site")