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
method = "GET"

category_mapping = {
    "여성패션": "1001",
    "남성패션": "1002",
    "뷰티": "1010",
    "출산/유아동": "1011",
    "완구/취미": "1012",
    "식품": "1013",
    "주방용품": "1014",
    "생활용품": "1015",
    "홈인테리어": "1016",
    "가전디지털": "1018",
    "스포츠/레저": "1019",
    "자동차용품": "1020",
    "반려동물": "1024"
}

all_products = []

for cat_name, cat_id in category_mapping.items():
    url = f"/v2/providers/affiliate_open_api/apis/openapi/products/bestcategories/{cat_id}?limit=20"
    authorization = generateHmac(method, url, SECRET_KEY, ACCESS_KEY)
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }
    
    response = requests.request(method=method, url=domain + url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        items = data.get('data', [])
        for item in items:
            item['my_category'] = cat_name 
            all_products.append(item)
            
    time.sleep(0.2) 

html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>초특가 핫딜</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; background-color: #f2f4f6; margin: 0; padding: 0; }
        .main-tabs { display: flex; justify-content: space-around; background: white; padding: 10px 0; border-bottom: 2px solid #f2f4f6; position: sticky; top: 0; z-index: 100;}
        .main-tab { font-size: 15px; font-weight: 700; color: #8b95a1; padding: 10px 20px; cursor: pointer; transition: 0.2s;}
        .main-tab.active { color: #1a1b1c; border-bottom: 3px solid #1a1b1c; }
        
        .category-tabs { display: flex; gap: 8px; overflow-x: auto; padding: 12px 16px; background: #fff; white-space: nowrap; border-bottom: 1px solid #e5e8eb;}
        .category-tabs::-webkit-scrollbar { display: none; }
        .sub-tab { padding: 8px 16px; background: #f2f4f6; border-radius: 20px; font-size: 13px; font-weight: 600; color: #4e5968; border: none; cursor: pointer; flex-shrink: 0;}
        .sub-tab.active { background: #3182f6; color: #fff; }
        
        .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 16px; }
        .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; text-decoration: none; color: inherit; }
        .item-img { width: 100%; aspect-ratio: 1; object-fit: cover; }
        .item-info { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
        .item-title { font-size: 13px; color: #333; line-height: 1.4; margin-bottom: 8px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .badge { display: inline-block; background: #ffe5e5; color: #e52528; font-size: 10px; font-weight: bold; padding: 3px 6px; border-radius: 4px; margin-bottom: 6px; width: fit-content; }
        
        /* 💡 추가된 가격 디자인 CSS */
        .price-wrap { display: flex; flex-direction: column; margin-top: auto; }
        .original-price { font-size: 11px; color: #8b95a1; text-decoration: line-through; margin-bottom: 2px; }
        .price-container { display: flex; align-items: baseline; gap: 4px; }
        .discount-rate { font-size: 16px; font-weight: 800; color: #e52528; }
        .item-price { font-size: 16px; font-weight: 800; color: #1a1b1c; }
        .time-ago { font-size: 11px; color: #8b95a1; margin-top: 6px; }
    </style>
</head>
<body>
    <div class="main-tabs">
        <div class="main-tab active">🔥 실시간 베스트</div>
        <div class="main-tab">🏆 투데이 특가</div>
        <div class="main-tab">🎯 맞춤 추천</div>
    </div>
    
    <div class="category-tabs">
        <div class="sub-tab active" onclick="filterItems(this, '전체')">전체</div>
        <div class="sub-tab" onclick="filterItems(this, '여성패션')">여성패션</div>
        <div class="sub-tab" onclick="filterItems(this, '남성패션')">남성패션</div>
        <div class="sub-tab" onclick="filterItems(this, '뷰티')">뷰티</div>
        <div class="sub-tab" onclick="filterItems(this, '출산/유아동')">출산/유아동</div>
        <div class="sub-tab" onclick="filterItems(this, '식품')">식품</div>
        <div class="sub-tab" onclick="filterItems(this, '생활용품')">생활용품</div>
        <div class="sub-tab" onclick="filterItems(this, '가전디지털')">가전/디지털</div>
        <div class="sub-tab" onclick="filterItems(this, '스포츠/레저')">스포츠/레저</div>
        <div class="sub-tab" onclick="filterItems(this, '반려동물')">반려동물</div>
        <div class="sub-tab" onclick="filterItems(this, '완구/취미')">완구/취미</div>
        <div class="sub-tab" onclick="filterItems(this, '주방용품')">주방용품</div>
        <div class="sub-tab" onclick="filterItems(this, '홈인테리어')">홈인테리어</div>
        <div class="sub-tab" onclick="filterItems(this, '자동차용품')">자동차용품</div>
    </div>

    <div class="grid-container" id="itemGrid">
"""

for item in all_products:
    title = item['productName']
    current_price = int(item['productPrice'])
    # 쿠팡 API에서 'basePrice'나 'originalPrice'를 찾아오고, 없으면 0으로 처리
    original_price = int(item.get('basePrice', item.get('originalPrice', 0)))
    
    link = item['productUrl']
    image_url = item['productImage']
    category_tag = item['my_category'] 
    
    # 💡 파이썬 자동 수학 계산기: 할인율(%) 구하기
    price_html = ""
    if original_price > current_price:
        discount_rate = int(((original_price - current_price) / original_price) * 100)
        price_html = f"""
            <div class="price-wrap">
                <div class="original-price"><del>{original_price:,}원</del></div>
                <div class="price-container">
                    <span class="discount-rate">{discount_rate}%</span>
                    <span class="item-price">{current_price:,}원</span>
                </div>
            </div>
        """
    else:
        # 할인이 안 들어간 상품은 그냥 현재 가격만 깔끔하게 보여줌
        price_html = f"""
            <div class="price-wrap">
                <div class="price-container">
                    <span class="item-price">{current_price:,}원</span>
                </div>
            </div>
        """
    
    html_content += f"""
        <a href="{link}" class="item-card" target="_blank" data-category="{category_tag}">
            <img src="{image_url}" class="item-img" alt="상품 이미지" loading="lazy">
            <div class="item-info">
                <div class="badge">실시간 순위권</div>
                <div class="item-title">{title}</div>
                {price_html}
                <div class="time-ago">쿠팡 베스트 상품</div>
            </div>
        </a>
    """
    
html_content += """
    </div>
    
    <script>
        function filterItems(element, category) {
            document.querySelectorAll('.sub-tab').forEach(tab => tab.classList.remove('active'));
            element.classList.add('active');
            
            const items = document.querySelectorAll('.item-card');
            items.forEach(item => {
                const itemCategory = item.getAttribute('data-category');
                if (category === '전체' || itemCategory === category) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
