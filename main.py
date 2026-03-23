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

# 가장 안정적인 베스트 API 코드 (판매량/인기순 자체 보장)
category_mapping = {
    "여성패션": "1001", "남성패션": "1002", "뷰티": "1010",
    "출산/유아동": "1011", "식품": "1013", "생활용품": "1015",
    "가전디지털": "1018", "스포츠/레저": "1019", "반려동물": "1024",
    "주방용품": "1014", "홈인테리어": "1016", "자동차용품": "1020"
}

category_bins = {cat: [] for cat in category_mapping.keys()}

for cat_name, cat_id in category_mapping.items():
    url = f"/v2/providers/affiliate_open_api/apis/openapi/products/bestcategories/{cat_id}"
    authorization = generateHmac(method, url, SECRET_KEY, ACCESS_KEY)
    headers = { "Authorization": authorization, "Content-Type": "application/json" }
    
    response = requests.request(method=method, url=domain + url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('data', [])[:20] 
        for item in items:
            item['my_category'] = cat_name 
            category_bins[cat_name].append(item)
    time.sleep(1) # 차단 방지 안전띠

# 랭킹 섞기 (1등부터 쭉 정렬)
all_products = []
rank_counter = 1
for i in range(20):
    for cat_name in category_mapping.keys():
        if i < len(category_bins[cat_name]):
            item = category_bins[cat_name][i]
            item['global_rank'] = rank_counter
            all_products.append(item)
            rank_counter += 1

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
        .main-tab { white-space: nowrap; font-size: 15px; font-weight: 700; color: #8b95a1; padding: 10px 15px; cursor: pointer; transition: 0.2s;}
        .main-tab.active { color: #1a1b1c; border-bottom: 3px solid #1a1b1c; }
        
        .category-tabs { display: flex; gap: 8px; overflow-x: auto; padding: 12px 16px; background: #fff; white-space: nowrap; border-bottom: 1px solid #e5e8eb;}
        .category-tabs::-webkit-scrollbar { display: none; }
        .sub-tab { white-space: nowrap; padding: 8px 16px; background: #f2f4f6; border-radius: 20px; font-size: 13px; font-weight: 600; color: #4e5968; border: none; cursor: pointer; flex-shrink: 0;}
        .sub-tab.active { background: #3182f6; color: #fff; }
        
        /* 💡 추가된 정렬 필터 UI */
        .filter-container { display: flex; justify-content: flex-end; padding: 10px 16px 0; }
        .sort-select { padding: 6px 12px; border-radius: 8px; border: 1px solid #d1d6db; background: white; font-size: 13px; color: #4e5968; font-weight: 600; outline: none; }
        
        .grid-container { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 16px; }
        .item-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; text-decoration: none; color: inherit; }
        
        .img-container { position: relative; width: 100%; aspect-ratio: 1; }
        .item-img { width: 100%; height: 100%; object-fit: cover; }
        .rank-badge { position: absolute; top: 8px; left: 8px; background: rgba(0,0,0,0.7); color: #fff; font-size: 14px; font-weight: 900; padding: 4px 8px; border-radius: 6px; z-index: 10; font-style: italic;}
        
        .item-info { padding: 12px; display: flex; flex-direction: column; flex-grow: 1; }
        .item-title { font-size: 13px; color: #333; line-height: 1.4; margin-bottom: 8px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
        .item-price { font-size: 16px; font-weight: 800; color: #1a1b1c; margin-top: auto; }
        .time-ago { font-size: 11px; color: #8b95a1; margin-top: 6px; }
    </style>
</head>
<body>
    <div class="main-tabs">
        <div class="main-tab active" onclick="alert('준비 중입니다!')">🔥 실시간 베스트</div>
        <div class="main-tab" onclick="alert('내일 오픈됩니다!')">🏆 투데이 특가</div>
        <div class="main-tab" onclick="alert('내일 오픈됩니다!')">🎯 맞춤 추천</div>
    </div>
    
    <div class="category-tabs">
        <div class="sub-tab active" onclick="filterItems(this, '전체')">전체</div>
        <div class="sub-tab" onclick="filterItems(this, '여성패션')">여성패션</div>
        <div class="sub-tab" onclick="filterItems(this, '남성패션')">남성패션</div>
        <div class="sub-tab" onclick="filterItems(this, '뷰티')">뷰티</div>
        <div class="sub-tab" onclick="filterItems(this, '식품')">식품</div>
        <div class="sub-tab" onclick="filterItems(this, '가전디지털')">가전/디지털</div>
        <div class="sub-tab" onclick="filterItems(this, '반려동물')">반려동물</div>
    </div>

    <div class="filter-container">
        <select class="sort-select" id="sortFilter" onchange="sortItems()">
            <option value="rank">🔥 인기순 (판매량)</option>
            <option value="lowPrice">💸 낮은 가격순</option>
            <option value="highPrice">💎 높은 가격순</option>
        </select>
    </div>

    <div class="grid-container" id="itemGrid">
"""

for item in all_products:
    title = item.get('productName', '상품명 없음')
    current_price = int(item.get('productPrice', 0))
    link = item.get('productUrl', '#')
    image_url = item.get('productImage', '')
    category_tag = item.get('my_category', '기타')
    rank_number = item.get('global_rank', 999) 
    
    # 정렬(Sort)을 위해 data-price, data-rank 속성을 몰래 심어둠
    html_content += f"""
        <a href="{link}" class="item-card" target="_blank" data-category="{category_tag}" data-price="{current_price}" data-rank="{rank_number}">
            <div class="img-container">
                <div class="rank-badge">{rank_number}</div>
                <img src="{image_url}" class="item-img" alt="상품 이미지" loading="lazy">
            </div>
            <div class="item-info">
                <div class="item-title">{title}</div>
                <div class="item-price">{current_price:,}원</div>
                <div class="time-ago">쿠팡 베스트 상품</div>
            </div>
        </a>
    """
    
html_content += """
    </div>
    
    <script>
        // 카테고리 필터 엔진
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
            // 카테고리 바꿀 때마다 정렬도 다시 맞춰줌
            sortItems();
        }

        // 💡 새롭게 추가된 정렬(Sorting) 엔진
        function sortItems() {
            const grid = document.getElementById('itemGrid');
            const sortType = document.getElementById('sortFilter').value;
            // 화면에 보이는 요소들만 모아서 배열로 만듦
            let items = Array.from(grid.querySelectorAll('.item-card'));
            
            items.sort((a, b) => {
                const priceA = parseInt(a.getAttribute('data-price'));
                const priceB = parseInt(b.getAttribute('data-price'));
                const rankA = parseInt(a.getAttribute('data-rank'));
                const rankB = parseInt(b.getAttribute('data-rank'));

                if (sortType === 'lowPrice') return priceA - priceB;
                if (sortType === 'highPrice') return priceB - priceA;
                return rankA - rankB; // rank (인기순 기본값)
            });
            
            // 정렬된 순서대로 화면에 다시 뿌려줌
            items.forEach(item => grid.appendChild(item));
        }
    </script>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
