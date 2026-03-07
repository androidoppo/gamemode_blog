import requests
import xml.etree.ElementTree as ET
import os
from slugify import slugify

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL = "HuggingFaceH4/zephyr-7b-beta"

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

headers = {
"Authorization": f"Bearer {HF_TOKEN}"
}

SITE_DIR="site"
os.makedirs(SITE_DIR,exist_ok=True)

# =====================
# AI呼び出し
# =====================

def ask_ai(prompt):

    payload={
    "inputs":prompt,
    "parameters":{
    "max_new_tokens":1200
    }
    }

    r=requests.post(API_URL,headers=headers,json=payload)

    data=r.json()

    if isinstance(data,list):
        return data[0]["generated_text"]

    return str(data)

# =====================
# Google Trends
# =====================

def get_trends():

    url="https://trends.google.com/trends/trendingsearches/daily/rss?geo=JP"

    # Google Trends may reject requests without a browser User-Agent or may return HTML error pages.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print("[WARN] Failed to fetch trends:", e)
        return ["テクノロジー", "ライフスタイル", "ビジネス"]

    if r.status_code != 200:
        print(f"[WARN] Trends request returned status {r.status_code}")
        return ["テクノロジー", "ライフスタイル", "ビジネス"]

    try:
        root = ET.fromstring(r.content)
    except ET.ParseError as e:
        snippet = r.text[:200].replace("\n", " ")
        print(f"[WARN] Failed to parse Trends RSS (first 200 chars): {snippet}")
        return ["テクノロジー", "ライフスタイル", "ビジネス"]

    topics = []
    for item in root.iter("title"):
        topics.append(item.text)

    return topics[:3]

# =====================
# タイトルAI
# =====================

def generate_title(topic):

    prompt=f"""
SEOブログタイトルを作ってください

テーマ:{topic}

30文字以内
"""

    title=ask_ai(prompt)

    return title.split("\n")[0].strip()

# =====================
# 記事生成AI
# =====================

def generate_article(topic):

    prompt=f"""
ブログ記事を書いてください

テーマ:{topic}

条件
・見出し付き
・1500〜2000文字
"""

    return ask_ai(prompt)

# =====================
# 修正AI
# =====================

def edit_article(article):

    prompt=f"""
次の記事を改善してください

条件
・読みやすく
・AIっぽさ削除
・誤字修正

記事
{article}
"""

    return ask_ai(prompt)

# =====================
# HTML生成AI
# =====================

def generate_html(title,article):

    prompt=f"""
次の記事をHTML body形式に変換してください

タイトル
{title}

記事
{article}

HTMLのみ
"""

    return ask_ai(prompt)

# =====================
# CSS生成AI
# =====================

def generate_css():

    prompt="""
シンプルなブログCSSを書いてください

レスポンシブ
読みやすい
"""

    return ask_ai(prompt)

# =====================
# 保存
# =====================

def save_site(title,html,css):

    slug=slugify(title)

    html_file=f"{SITE_DIR}/{slug}.html"
    css_file=f"{SITE_DIR}/{slug}.css"

    page=f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<title>{title}</title>

<link rel="stylesheet" href="{slug}.css">

</head>

<body>

{html}

</body>

</html>
"""

    with open(html_file,"w",encoding="utf8") as f:
        f.write(page)

    with open(css_file,"w",encoding="utf8") as f:
        f.write(css)

    print("created",html_file)

# =====================
# WordPress投稿
# =====================

def post_wordpress(title,article):

    url="http://localhost/wp-json/wp/v2/posts"

    user="admin"
    password="APPLICATION_PASSWORD"

    data={
    "title":title,
    "content":article,
    "status":"draft"
    }

    requests.post(
    url,
    json=data,
    auth=(user,password)
    )

# =====================
# Netlify deploy
# =====================

def deploy_netlify():

    import subprocess

    subprocess.run(["git","add","."])
    subprocess.run(["git","commit","-m","AI article"])
    subprocess.run(["git","push"])

# =====================
# MAIN
# =====================

def run():

    print("AI Blog Factory Start")

    topics=get_trends()

    for topic in topics:

        print("topic:",topic)

        title=generate_title(topic)

        article=generate_article(topic)

        article=edit_article(article)

        html=generate_html(title,article)

        css=generate_css()

        save_site(title,html,css)

        post_wordpress(title,article)

    deploy_netlify()

    print("DONE")

run()