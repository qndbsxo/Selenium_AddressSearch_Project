# 네이버 지도 데이터 수집하기
from selenium import webdriver  # 웹 자동화
from selenium.webdriver.common.keys import Keys  # to input text

# from collections import OrderedDict, Counter
import pandas as pd  # to DataFrame
import time
from win10toast import ToastNotifier  # to Notification

# set option
options = webdriver.ChromeOptions()
# 사람처럼 보이게 하는 옵션들
options.add_argument("--headless")
options.add_argument("disable-gpu")  # 가속 사용x
options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재

driver = webdriver.Chrome("chromedriver.exe")  # 드라이버 생성

df = pd.read_csv("133.인천광역시_서구_식품관련업_20210702_검색완료.csv", encoding="cp949")[1303:2213]
df = df[df["Result"] == "X"]
df["도로명"] = df["소재지(도로명)"].str.split(" ", expand=True)[2]  # 도로명 주소


# 네이버 지도 접속
driver.get("https://map.naver.com/v5/search")

result = []
for i in range(2100, 2700):
    try:
        time.sleep(1)
        search_box = driver.find_element_by_css_selector(
            "div.input_box>input.input_search"
        )  # 검색상자 선택
        search_box.clear()  # 검색상자 지우기
        temp_name = df.loc[i, "업소명"]
        temp_road_name = df.loc[i, "도로명"]
        search_box.send_keys("인천 서구 " + temp_name)
        # 검색버튼 누르기 // 검색버튼: button.spm
        search_box.send_keys(Keys.ENTER)
        time.sleep(1)
        # 컨테이너(가게 정보 ) 수
        # stores = driver.find_element_by_css_selector("div.lsnx").text # 수정할 부분
        stores = driver.find_element_by_xpath(
            "/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li[1]/div[1]/dl/dd[1]"
        ).text

        # 도로명이 포함된 경우만 저장
        if temp_road_name in stores:
            result.append(stores)
            print(i, result[-1])

        else:
            result.append("x")
            print(i, "x")

    except Exception as e:
        result.append("x")
        print(i, "-", "Exception", "-", e)
    finally:
        # DataFrame to save csvfile
        result_to_df = pd.DataFrame(data=result, columns=["네이버맵 검증"])
        merge_result_and_df = pd.concat(objs=[df, result_to_df], axis=1)
        merge_result_and_df.to_csv("인천광역시_서구_식품관련업_네이버맵.csv", encoding="cp949")

        print(i, "finally")

# Notification
notifierToast = ToastNotifier()
notifierToast.show_toast("서구 식품접객업소 신고현황 점검완료")
