# 네이버 지도 데이터 수집하기
from pandas.core.frame import DataFrame
from selenium import webdriver  # 웹 자동화
from selenium.webdriver.common.keys import Keys  # to input text

# from collections import OrderedDict, Counter
import pandas as pd  # to DataFrame
import time
from win10toast import ToastNotifier  # to Notification

# set option
options = webdriver.ChromeOptions()
## 사람처럼 보이게 하는 옵션들
options.add_argument("--headless")
options.add_argument("disable-gpu")  # 가속 사용x
options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재

driver = webdriver.Chrome("chromedriver.exe")  # 드라이버 생성
df = pd.read_excel("119.인천광역시_공중위생업소_서구_20210721_카카오맵 네이버맵점검완료_윤태.xlsx").reset_index()[
    :694
]
col_road_names = df["영업소 주소(도로명)"].str.split(" ", expand=True)[2].to_frame()
df = pd.concat([df, col_road_names], axis=1).rename(columns={2: "도로명"})

# 카카오지도 접속
driver.get("https://map.kakao.com/")

# 검색창에 검색어 입력하기 // 검색창: #search\.keyword\.query
result = []
for i in range(len(df)):
    try:
        # 검색상자 선택
        time.sleep(1)
        search_box = driver.find_element_by_css_selector(
            "#search\.keyword\.query"
        )  # 검색상자 선택
        search_box.clear()  # 검색상자 지우기
        temp_name = df.loc[i, "업소명"]
        temp_road_name = df.loc[i, "도로명"]
        search_box.send_keys("인천 서구 " + temp_name)
        # 검색버튼 누르기 // 검색버튼: //*[@id="search.keyword.submit"]
        search_button = driver.find_element_by_css_selector("#search\.keyword\.submit")
        # time.sleep(1)
        search_button.send_keys(Keys.ENTER)
        time.sleep(1)
        # # 컨테이너(가게 정보 ) 수 // 주소 element: #info\.search\.place\.list > li:nth-child(1) > div.info_item > div.addr > p:nth-child(1)
        # TODO:
        stores = driver.find_element_by_css_selector(
            "#info\.search\.place\.list > li:nth-child(1) > div.info_item > div.addr > p:nth-child(1)"
        ).text  # 수정할 부분

        # 도로명이 포함된 경우만 저장
        if temp_road_name in stores:
            result.append(stores)
            print(i, stores)
        # 도로명이 포함X 경우만 저장
        else:
            result.append("x")
            print(i, "x")
    except Exception as e:
        result.append("x")
        print(i, e)


result_to_df = pd.DataFrame(data=result, columns=["네이버맵 검증"])
result_df = pd.concat(objs=[df, result_to_df], axis=1)
result_df.to_csv("120.인천광역시_서구_식품접객업소(신고현황)_카카오맵점검+네이버맵점검(최종).csv")

# 스크립트 실행 후 완료 알림 보내기
notifierToast = ToastNotifier()
notifierToast.show_toast("네이버맵 점검완료",)
