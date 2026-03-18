import hmac
import hashlib
import os
import time
import requests
from time import gmtime, strftime

# 💡 깃허브 비밀금고에서 내 키를 안전하게 불러오는 마법의 코드!
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
        <title>초특가 핫딜 큐레이션</title>
        <style>
            body { font-family: 'Malgun Gothic', sans-serif; background-color: #f2f4f6; margin: 0; padding: 16px; }
            .header { text-align: center; font-size: 20px; font-weight: bold; color: #333; margin-bottom: 20px; }
            .item-card { background: white; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; }
            .item-img { width: 100%; height: 180px; object-fit: cover; border-radius: 12px 12px 0 0; }
            .item-content { padding: 16px; }
            .item-title { font-size: 15px; font-weight: bold; color: #333; margin-bottom: 8px; line-height: 1.4; }
            .item-price { font-size: 18px; color: #e52528; font-weight: bold; margin-bottom: 12px; }
            .buy-btn { display: block; text-align: center; background-color: #3182f6; color: white; text-decoration: none; padding: 14px; border-radius: 8px; font-weight: bold; font-size: 16px; margin: 0 16px 16px 16px;}
        </style>
    </head>
    <body>
        <div class="header">🔥 오늘의 초특가 핫딜</div>
    """
    
    for item in items[:10]: 
        title = item['productName']
        price = f"{item['productPrice']:,}"
        link = item['productUrl']
        image_url = item['productImage']
        
        html_content += f"""
        <div class="item-card">
            <img src="{image_url}" class="item-img" alt="{title}">
            <div class="item-content">
                <div class="item-title">{title}</div>
                <div class="item-price">{price}원</div>
            </div>
            <a href="{link}" class="buy-btn" target="_blank">토스페이로 특가 확인하기</a>
        </div>
        """
        
    html_content += """
    </body>
    </html>
    """
    
    # 💡 네틀리파이용 파일 이름인 'index.html'로 저장되도록 수정했어!
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

else:
    print("API 요청 실패:", response.status_code)
