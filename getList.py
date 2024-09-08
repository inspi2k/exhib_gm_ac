from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import chromedriver_autoinstaller
import pandas as pd


chromedriver_autoinstaller.install()

options = Options()
# options.add_argument('--headless')  # 헤드리스 모드 (브라우저 창 안 띄우기)

# 웹 드라이버 초기화
driver = webdriver.Chrome(options=options)

# URL 설정
channel = [
    {'name':'gmarket', 'url':'http://rpp.gmarket.co.kr/?exhib=179136', 'buy_counter':'buy_counter_bx'},
    {'name':'auction', 'url':'http://rpp.auction.co.kr/?exhib=179137', 'buy_counter':'amount'},
]
excel_file = f'list_{datetime.now().strftime("%y%m%d_%H%M%s")}.xlsx'

for ch in channel:
    
    driver.get(ch['url'])

    try:
        # 페이지 로딩 대기 (최대 10초) - 로딩 완료 되면 즉시 다음 코드 실행
        driver.implicitly_wait(10)

        # 카테고리 추출
        categories = []
        items = driver.find_elements(By.CSS_SELECTOR, 'div.module_navi div.item')

        for item in items:
            name = item.find_element(By.CSS_SELECTOR, 'span.tit > span').text
            anchor = item.find_element(By.CSS_SELECTOR, 'a.navi_anchor').get_attribute('href')

            categories.append({
                'name': name,
                'anchor': anchor,
            })
        
        # for category in categories:
        #     print(f'Name: {category["name"]}')
        #     print(f'Anchor: {category["anchor"]}')
        #     print()

        # 상품 더보기 버튼이 존재하는지 확인
        while (len(driver.find_elements(By.CSS_SELECTOR, 'div.button_wrap')) != 0):
            # 상품 더보기 버튼 클릭
            driver.find_element(By.CSS_SELECTOR, 'button.btn_more').click()

            # 해당 엘리먼트가 로딩될 때까지 대기
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.item')))
        
        # 추가로 상품이 로딩되도록 3초 대기
        # time.sleep(3)
        # ===== 이미 시간을 잡아 먹고 있음

        # 상품 리스트
        products = []
        for category in categories[1:]:
            css_anchor = category['anchor'].split('#')[1]
            # print(category['name'], end='\t', flush=True)
            # try:
            #     driver.find_element(By.CSS_SELECTOR, f'#{css_anchor} + div.module_item')
            #     # EC.presence_of_element_located((By.CSS_SELECTOR, f'#{css_anchor} + div.module_item'))
            # except:
            #     continue

            items = driver.find_elements(By.CSS_SELECTOR, f'#{css_anchor} + div.module_item ul.products-list li.elements_item')
            # print(css_anchor, len(items.find_elements(By.CSS_SELECTOR, 'li.elements_item')))

            for item in items:
                product_code = item.get_attribute('data-goods-no')
                title = item.find_element(By.CSS_SELECTOR, 'a.title').text
                url = item.find_element(By.CSS_SELECTOR, 'a.title').get_attribute('href')
                price_origin = item.find_element(By.CSS_SELECTOR, 'li.origin .num').text
                price_selling = item.find_element(By.CSS_SELECTOR, 'li.selling strong').text
                delivery = item.find_element(By.CSS_SELECTOR, 'div.add-info .box').text
                buy_counter = item.find_element(By.CSS_SELECTOR, f'div.{ch["buy_counter"]} span').text
                # img_url = item.find_element(By.CSS_SELECTOR, 'div.elements_img a img').get_attribute('src')
                # ===== 주류 adult_box 처리해야함

                products.append({
                    'cate_name': category['name'],
                    'product_code': product_code,
                    'title': title,
                    'url': url,
                    'price_origin': price_origin,
                    'price_selling': price_selling,
                    'delivery': delivery,
                    'buy_counter': buy_counter,
                    # 'img_url': img_url,
                })
                print('.', end='', flush=True)
            print()

        # 딕셔너리 리스트를 데이터프레임으로 변환
        df = pd.DataFrame(products)

        # 데이터프레임을 엑셀 파일로 저장
        mode = 'w' if (ch == channel[0]) else 'a'
        with pd.ExcelWriter(excel_file, mode=mode, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=ch['name'])
            print(f'List Export - {excel_file} / {ch["name"]}')

    except Exception as e:
        print(e)

    # finally:
# 웹 드라이버 종료
driver.quit()