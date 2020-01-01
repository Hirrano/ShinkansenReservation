import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

####################################################################
path_chrome_driver = 'C:\module\express-yoyaku\chromedriver.exe'
url = 'https://shinkansen1.jr-central.co.jp/RSV_P/index.htm'
user_id = '★input here★'
password = '★input here★'
month_day = '12月31日（火）' #カッコは全角じゃないと動かない。
hour = '09'
minute = '00' #00,15,30,45から選択
start_station = '010' #駅番号は下記のコメントを参照
dest_station = '160' #駅番号は下記のコメントを参照
# 010  東　京    020  品　川    030  新横浜    040  小田原    050  熱　海    060  三　島    070  新富士
# 080  静　岡    090  掛　川    100  浜　松    110  豊　橋    120  三河安城    130  名古屋    140  岐阜羽島
# 150  米　原    160  京　都    170  新大阪    180  新神戸    190  西明石    200  姫　路    210  相　生
# 220  岡　山    230  新倉敷    240  福　山    250  新尾道    260  三　原    270  東広島    280  広　島
# 290  新岩国    300  徳　山    310  新山口    320  厚　狭    350  博　多    330  新下関    340  小　倉
####################################################################

def open_url():
    driver = webdriver.Chrome(executable_path=path_chrome_driver)
    driver.get(url)

    id_box = driver.find_element_by_id("pw-2")
    id_box.send_keys(user_id)
    password_box = driver.find_element_by_id("pw-1")
    password_box.send_keys(password)
    submit_box = driver.find_element_by_id("sb-1")
    submit_box.click()

    yoyaku_href = driver.find_element_by_name("b-1")
    yoyaku_href.click()
    return driver

def input_parameter(driver):
    # 日付
    month_day_select = Select(driver.find_element_by_id("s-2"))
    month_day_select.select_by_value(month_day)

    # 時
    hour_select = Select(driver.find_element_by_id("s-3"))
    hour_select.select_by_value(hour)

    # 分
    minitute_select = Select(driver.find_element_by_id("s-4"))
    minitute_select.select_by_value(minute)

    # 出発/到着はデフォルトの出発のみ

    # 乗車駅
    start_station_select = Select(driver.find_element_by_id("s6"))
    start_station_select.select_by_value(start_station)

    # 降車駅
    dest_station_select = Select(driver.find_element_by_id("s7"))
    dest_station_select.select_by_value(dest_station)

    # 大人人数は１人のみ対応（デフォルト）
    # こども人数は対応しない
    # ひかり・さくら・こだまのみ検索　は対応しない
    # e特急券を利用するのは対応しない
    # カレンダーから選択は対応しない
    # 列車名指定は対応しない
    # ボタン押下
    time.sleep(1)
    submit_box = driver.find_element_by_id("sb-1")
    submit_box.click()


def choose_seat(driver):
    loop_break_flag = False
    # ページを１～６で開く
    for page in range(1,6):
        # ページ内ダイアログ１～６開く
        for idx in range(1,6):
            kouho_sentaku_css_mae = '#main > form > section.sub-contents.float-right > article:nth-child('
            kouho_sentaku_css_ato = ') > div > div.manku > p'
            kouho_sentaku_css_selector = kouho_sentaku_css_mae+str(idx)+kouho_sentaku_css_ato
            print(kouho_sentaku_css_selector)
            kouho_sentaku_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, kouho_sentaku_css_selector)))
            # kouho_sentaku_button = driver.find_element_by_css_selector(kouho_sentaku_css_selector)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            kouho_sentaku_button.click()

            # 喫煙ルーム近くの選択肢も表示させる
            display_control_select = Select(driver.find_element_by_id("s-"+str(idx)))
            display_control_select.select_by_value('3')

            target_list = [
                '#c-mrad-0-1-'+str(idx),#　→指定席、普通車
                '#c-mrad-0-2-'+str(idx),#→指定席、グリーン車
                '#c-mrad-1-1-'+str(idx),#→喫煙ルーム近く、指定席、普通車
                '#c-mrad-1-2-'+str(idx),#→喫煙ルーム近く、指定席、グリーン車
        #        '#c-mrad-2-1-'+str(idx),#→自由席、普通車→見ない
        #        '#c-mrad-2-2-'+str(idx),#→自由席にグリーンは存在しない
                ]
            for target in target_list:
                try:
                    # time.sleep(1)
                    input = driver.find_element_by_css_selector(target)
                    input.click()
                    loop_break_flag = True
                    break
                except:
                    print('no element : '+target)
            # ダイアログクローズ
            if not loop_break_flag:
                dialog_close_button = driver.find_element_by_id("l-6")
                dialog_close_button.click()
                # time.sleep(1)
            if loop_break_flag:
                break
        # 次ページへ遷移（１～６ページで遷移）
        if not loop_break_flag:
            next_page_button = driver.find_element_by_id("l-2")
            next_page_button.click()
        if loop_break_flag:
            break
    return loop_break_flag

####################################################################

driver = open_url()
input_parameter(driver)
flag = False
for index in range(300):
    flag = choose_seat(driver)
    if not flag:
        if index == 100:
            raise Exception
        time.sleep(1)
        back_button = driver.find_element_by_id('b-2')
        back_button.click()
        input_parameter(driver)


# 座席決定
submit_box = driver.find_element_by_id("sb-2")
submit_box.click()

# 購入ボタン
# submit_box = driver.find_element_by_id("sb-1")
# submit_box.click()

# comment

