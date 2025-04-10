import requests
from bs4 import BeautifulSoup
import time
import hashlib
import os

URL = 'https://www.hermes.com/tw/zh/category/women/bags-and-small-leather-goods/all-bags/'
LINE_NOTIFY_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN")
LAST_HASH_FILE = 'last_hash.txt'

def fetch_product_list():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    items = soup.select('li.product-item')
    for item in items:
        name_tag = item.select_one('.product-item-name')
        img_tag = item.select_one('img')
        link_tag = item.find('a', href=True)

        if name_tag and img_tag and link_tag:
            name = name_tag.get_text(strip=True)
            img_url = img_tag['src']
            link = 'https://www.hermes.com' + link_tag['href']
            products.append({
                'name': name,
                'img': img_url,
                'link': link
            })
    return products

def get_products_hash(products):
    content = ''.join([p['name'] for p in products])
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def load_last_hash():
    try:
        with open(LAST_HASH_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''

def save_current_hash(current_hash):
    with open(LAST_HASH_FILE, 'w') as f:
        f.write(current_hash)

def send_line_notify(products):
    for p in products[:5]:
        message = f"【新品上架】{p['name']}\n{p['link']}\n圖片：{p['img']}"
        headers = {
            "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
        }
        data = {
            'message': message
        }
        requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

def check_update():
    print("正在檢查新品...")
    products = fetch_product_list()
    if not products:
        print("找不到商品")
        return

    current_hash = get_products_hash(products)
    last_hash = load_last_hash()

    if current_hash != last_hash:
        print("發現新商品！")
        send_line_notify(products)
        save_current_hash(current_hash)
    else:
        print("無新商品")

if __name__ == '__main__':
    check_update()
