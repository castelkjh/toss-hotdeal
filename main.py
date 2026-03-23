import hmac
import hashlib
import os
import time
import requests
from time import gmtime, strftime

ACCESS_KEY = os.environ.get('COUPANG_ACCESS')
SECRET_KEY = os.environ.get('COUPANG_SECRET')

def generateHmac(method, url, secretKey, accessKey):
    os.environ['TZ'] = 'GMT+0'
    time.tzset()
    datetime = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'
    message = datetime + method + url
    signature = hmac.new(bytes(secretKey, "utf-8"),
                         message.encode("utf-8"),
                         hashlib.sha256).hexdigest()
    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(accessKey, datetime, signature)

domain = "https://api-gateway.coupang.com"
url = "/v2/providers/affiliate_open_api/apis/openapi/products/goldbox"
method = "GET"

authorization = generateHmac(method, url, SECRET_KEY, ACCESS_KEY)
headers = {
    "Authorization": authorization,
    "Content-Type": "application/json"
}

response = requests.request(method=method, url=domain + url, headers=headers)

if response.status_code == 200:
    data = response.json()
    items = data.get('data', [])
    
    # 상단 탭 및 2열 그리드 UI가 적용된 세련된 HTML 뼈대
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>초특가 핫딜</title>
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; background-color: #f2f4f6; margin: 0; padding: 0; }
            .header-banner { background: white; padding: 15px; text-align: center; font-size: 18px; font-weight: 800; color: #333; position: sticky; top: 0; z-index: 100; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            /* 상단 카테고리 탭 디자인 */
            .category-tabs { display: flex; gap: 8px; overflow-x: auto; padding: 12px 16px; background: #fff; white-space: nowrap; border-bottom: 1px solid #e5e8eb;}
            .category-tabs::-webkit-scrollbar { display: none; }
            .tab { padding: 8px 16px; background: #f2f4f6; border-radius: 20px; font-size: 14px; font-weight: 600; color: #4e5968; text-decoration: none; border: none; cursor: pointer;}
            .tab.active { background: #1a1b1c; color: #fff; }
            /* 2열 그리드(바둑판) 디자인 */
            .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 16px; }
            .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; text-decoration: none; color: inherit;}
            .item-img { width: 100%; aspect-ratio: 1; object-fit: cover; }
            .item-info { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
            .item-title { font-size: 13px; color: #333; line-height: 1.4; margin-bottom: 8px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
            .badge { display: inline-block; background: #ffe5e5; color: #e52528; font-size: 10px; font-weight: bold; padding: 3px 6px; border-radius: 4px; margin-bottom: 6px; width: fit-content; }
            .item-price { font-size: 16px; font-weight: 800; color: #1a1b1c; margin-top: auto; }
        </style>
    </head>
    <body>
        <div class="header-banner">🔥 실시간 초특가 랭킹</div>
        
        <div class="category-tabs">
            <div class="tab active">전체</div>
            <div class="tab">디지털/가전</div>
            <div class="tab">식품/생활</div>
            <div class="tab">패션/뷰티</div>
        </div>

        <div class="grid-container">
    """
    
    # 상품을 2열 바둑판 형태로 뿌려주기
    for item in items[:16]: # 짝수(16개)로 맞춰서 배열이 예쁘게 떨어지도록 수정
        title = item['productName']
        price = f"{item['productPrice']:,}"
        link = item['productUrl']
        image_url = item['productImage']
        
        html_content += f"""
            <a href="{link}" class="item-card" target="_blank">
                <img src="{image_url}" class="item-img" alt="상품 이미지">
                <div class="item-info">
                    <div class="badge">오늘만 특가</div>
                    <div class="item-title">{title}</div>
                    <div class="item-price">{price}원</div>
                </div>
            </a>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

else:
    print("API 요청 실패:", response.status_code)
