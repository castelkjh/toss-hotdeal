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
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>초특가 핫딜</title>
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; background-color: #f2f4f6; margin: 0; padding: 0; }
            /* 1단: 메인 탭 (실시간/인기/연령별) */
            .main-tabs { display: flex; justify-content: space-around; background: white; padding: 10px 0; border-bottom: 2px solid #f2f4f6; position: sticky; top: 0; z-index: 100;}
            .main-tab { font-size: 15px; font-weight: 700; color: #8b95a1; padding: 10px 20px; cursor: pointer; transition: 0.2s;}
            .main-tab.active { color: #1a1b1c; border-bottom: 3px solid #1a1b1c; }
            
            /* 2단: 서브 카테고리 (가로 스크롤) */
            .category-tabs { display: flex; gap: 8px; overflow-x: auto; padding: 12px 16px; background: #fff; white-space: nowrap; border-bottom: 1px solid #e5e8eb;}
            .category-tabs::-webkit-scrollbar { display: none; }
            .sub-tab { padding: 8px 16px; background: #f2f4f6; border-radius: 20px; font-size: 13px; font-weight: 600; color: #4e5968; border: none; cursor: pointer;}
            .sub-tab.active { background: #3182f6; color: #fff; } /* 토스 블루 컬러로 포인트 */
            
            /* 2열 바둑판 리스트 */
            .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 16px; }
            .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; text-decoration: none; color: inherit;}
            .item-img { width: 100%; aspect-ratio: 1; object-fit: cover; }
            .item-info { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
            .item-title { font-size: 13px; color: #333; line-height: 1.4; margin-bottom: 8px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
            .badge { display: inline-block; background: #ffe5e5; color: #e52528; font-size: 10px; font-weight: bold; padding: 3px 6px; border-radius: 4px; margin-bottom: 6px; width: fit-content; }
            .item-price { font-size: 16px; font-weight: 800; color: #1a1b1c; margin-top: auto; }
            .time-ago { font-size: 11px; color: #8b95a1; margin-top: 4px; }
        </style>
    </head>
    <body>
        <div class="main-tabs">
            <div class="main-tab active" onclick="changeMain(this)">🔥 실시간</div>
            <div class="main-tab" onclick="changeMain(this)">🏆 베스트</div>
            <div class="main-tab" onclick="changeMain(this)">🎯 연령별</div>
        </div>
        
        <div class="category-tabs">
            <div class="sub-tab active" onclick="changeSub(this)">전체</div>
            <div class="sub-tab" onclick="changeSub(this)">디지털/가전</div>
            <div class="sub-tab" onclick="changeSub(this)">생활/식품</div>
            <div class="sub-tab" onclick="changeSub(this)">패션/의류</div>
            <div class="sub-tab" onclick="changeSub(this)">뷰티</div>
        </div>

        <div class="grid-container">
    """
    
    for item in items[:16]:
        title = item['productName']
        # 💡 피드백 1번 반영: int()로 감싸서 소수점(.0) 완벽 제거
        price = f"{int(item['productPrice']):,}"
        link = item['productUrl']
        image_url = item['productImage']
        
        html_content += f"""
            <a href="{link}" class="item-card" target="_blank">
                <img src="{image_url}" class="item-img" alt="상품 이미지">
                <div class="item-info">
                    <div class="badge">오늘만 특가</div>
                    <div class="item-title">{title}</div>
                    <div class="item-price">{price}원</div>
                    <div class="time-ago">방금 전 업데이트</div>
                </div>
            </a>
        """
        
    html_content += """
        </div>
        
        <script>
            function changeMain(element) {
                document.querySelectorAll('.main-tab').forEach(tab => tab.classList.remove('active'));
                element.classList.add('active');
            }
            function changeSub(element) {
                document.querySelectorAll('.sub-tab').forEach(tab => tab.classList.remove('active'));
                element.classList.add('active');
            }
        </script>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

else:
    print("API 요청 실패:", response.status_code)
