import requests
import xml.etree.ElementTree as ET
import os
import markdown
import subprocess
import hashlib
import time
from bs4 import BeautifulSoup

# =====================
# CONFIG
# =====================

HF_TOKEN = os.getenv("HF_TOKEN")

MODEL = "HuggingFaceH4/zephyr-7b-beta"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

SITE_URL = os.getenv("SITE_URL", "https://example.netlify.app")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

SITE_DIR = "site"
MD_DIR = "markdown"

os.makedirs(SITE_DIR, exist_ok=True)
os.makedirs(MD_DIR, exist_ok=True)

# TCP connection reuse
session = requests.Session()

# =====================
# AI API
# =====================

def ask_ai(prompt, retries=3):

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 900}
    }

    for i in range(retries):

        try:

            r = session.post(API_URL, headers=HEADERS, json=payload, timeout=60)

            if r.status_code == 200:

                data = r.json()

                if isinstance(data, list):

                    return clean_ai_text(data[0]["generated_text"])

                return clean_ai_text(str(data))

            print("AI API error:", r.status_code)

        except Exception as e:

            print("AI request failed:", e)

        time.sleep(5)

    return ""

# =====================
# AI TEXT CLEAN
# =====================

def clean_ai_text(text):

    lines = text.split("\n")

    filtered = []

    for line in lines:

        l = line.lower()

        if l.startswith("sure"):
            continue

        if l.startswith("here is"):
            continue

        filtered.append(line)

    return "\n".join(filtered)

# =====================
# SEARCH API
# =====================

from pytrends.request import TrendReq

def get_trends():

    print("Fetching trends (pytrends)...")

    try:

        pytrends = TrendReq(hl='ja-JP', tz=540)

        df = pytrends.trending_searches(pn='japan')

        topics = df[0].tolist()[:5]

        print("Trends:", topics)

        return topics

    except Exception as e:

        print("Trends error:", e)

        return ["AI副業", "生成AI", "Python自動化"]

# =====================
# SLUG
# =====================

def make_slug(title):

    import hashlib

    slug = title.lower().replace(" ", "-")

    h = hashlib.md5(title.encode()).hexdigest()

    return f"{slug}-{h[:6]}"

# =====================
# DUPLICATE
# =====================

def already_exists(slug):

    return os.path.exists(f"{SITE_DIR}/{slug}.html")

# =====================
# WRITER AI
# =====================

def writer_ai(topic):

    print("Writer:", topic)

    prompt = f"""
ブログ記事を書いてください

テーマ: {topic}

条件
Markdown形式
見出し付き
1500文字以上
"""

    return ask_ai(prompt)

# =====================
# EDITOR AI
# =====================

def editor_ai(md):

    print("Editor")

    prompt = f"""
次の記事を編集してください

条件
読みやすくする
誤字修正
AIっぽさ削除

{md}
"""

    return ask_ai(prompt)

# =====================
# SEO AI
# =====================

def seo_ai(md):

    print("SEO")

    prompt = f"""
次の記事をSEO向けに改善してください

条件
h2構造整理
重要語を**強調**
段落を整理

Markdown形式維持

{md}
"""

    return ask_ai(prompt)

# =====================
# SAVE MARKDOWN
# =====================

def save_markdown(slug, md):

    path = f"{MD_DIR}/{slug}.md"

    with open(path, "w", encoding="utf8") as f:

        f.write(md)

    print("Saved MD:", path)

# =====================
# MARKDOWN → HTML
# =====================

def md_to_html(md):

    return markdown.markdown(md)

# =====================
# CLEAN HTML
# =====================

def clean_html(html):

    try:

        soup = BeautifulSoup(html, "html.parser")

        return soup.prettify()

    except:

        return html

# =====================
# SAVE HTML
# =====================

def save_html(slug, title, html):

    path = f"{SITE_DIR}/{slug}.html"

    page = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>

{html}

</body>
</html>
"""

    with open(path, "w", encoding="utf8") as f:

        f.write(page)

    print("Saved HTML:", path)

# =====================
# SITEMAP
# =====================

def generate_sitemap():

    print("Generating sitemap")

    urls = []

    for f in os.listdir(SITE_DIR):

        if f.endswith(".html"):

            urls.append(f"{SITE_URL}/{f}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for url in urls:

        xml += "<url>\n"
        xml += f"<loc>{url}</loc>\n"
        xml += "</url>\n"

    xml += "</urlset>"

    with open(f"{SITE_DIR}/sitemap.xml", "w") as f:

        f.write(xml)

# =====================
# GIT PUSH
# =====================

def git_push():

    print("Git push")

    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "AI article"])
    subprocess.run(["git", "push"])

# =====================
# MAIN
# =====================

def run():

    print("AI BLOG FACTORY START")

    topics = get_trends()

    for topic in topics:

        print("----------------")

        slug = make_slug(topic)

        if already_exists(slug):

            print("Duplicate skip:", slug)

            continue

        md = writer_ai(topic)

        if not md:
            print("Writer failed")
            continue

        md = editor_ai(md)

        md = seo_ai(md)

        save_markdown(slug, md)

        html = md_to_html(md)

        html = clean_html(html)

        save_html(slug, topic, html)

        time.sleep(3)

    generate_sitemap()

    git_push()

    print("DONE")


if __name__ == "__main__":
    run()