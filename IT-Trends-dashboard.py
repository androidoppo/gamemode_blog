import requests
import feedparser
from collections import defaultdict

# =========================
# ダッシュボード設定
# =========================

CONFIG = {

    "DISPLAY_LIMIT": 30,

    "REDDIT_LIMIT": 50,
    "HACKERNEWS_LIMIT": 50,
    "QIITA_LIMIT": 50,
    "GITHUB_LIMIT": 50,
    "GOOGLE_TRENDS_LIMIT": 40,

    "SHORT_TITLE": True,
    "TITLE_MAX_LEN": 40,

    # 追加
    "SHOW_SOURCE": False,
    "SHOW_SCORE": False,
    "ONE_LINE_MODE": True
}

# =========================
# ITキーワード
# =========================

IT_KEYWORDS = [
    "AI","ChatGPT","OpenAI","Claude","Gemini",
    "Apple","iPhone","Mac","iPad",
    "Google","Android","Pixel",
    "Microsoft","Windows",
    "NVIDIA","AMD","Intel",
    "GPU","CPU","半導体",
    "Python","GitHub","Linux"
]

# =========================
# Google Trends
# =========================

def get_google_trends():

    url = "https://trends.google.com/trending/rss?geo=JP"

    feed = feedparser.parse(url)

    results = []

    for entry in feed.entries[:CONFIG["GOOGLE_TRENDS_LIMIT"]]:

        results.append({
            "title": entry.title,
            "source": "GoogleTrends",
            "score": 3
        })

    return results


# =========================
# Hacker News
# =========================

def get_hackernews():

    url = "https://hn.algolia.com/api/v1/search?tags=front_page"

    results = []

    try:

        data = requests.get(url).json()

        for item in data["hits"][:CONFIG["HACKERNEWS_LIMIT"]]:

            title = item.get("title")

            if title:

                results.append({
                    "title": title,
                    "source": "HackerNews",
                    "score": 2
                })

    except:
        pass

    return results


# =========================
# Reddit
# =========================

def get_reddit():

    url = f"https://www.reddit.com/r/technology/top.json?limit={CONFIG['REDDIT_LIMIT']}"

    headers = {"User-Agent":"trend-dashboard"}

    results = []

    try:

        data = requests.get(url, headers=headers).json()

        for post in data["data"]["children"]:

            title = post["data"]["title"]

            results.append({
                "title": title,
                "source": "Reddit",
                "score": 2
            })

    except:
        pass

    return results


# =========================
# Qiita
# =========================

def get_qiita():

    url = f"https://qiita.com/api/v2/items?page=1&per_page={CONFIG['QIITA_LIMIT']}"

    results = []

    try:

        data = requests.get(url).json()

        for item in data:

            results.append({
                "title": item["title"],
                "source": "Qiita",
                "score": 1
            })

    except:
        pass

    return results


# =========================
# GitHub
# =========================

def get_github():

    url = "https://ghapi.huchen.dev/repositories"

    results = []

    try:

        data = requests.get(url).json()

        for repo in data[:CONFIG["GITHUB_LIMIT"]]:

            title = repo["name"]

            results.append({
                "title": title,
                "source": "GitHub",
                "score": 2
            })

    except:
        pass

    return results


# =========================
# ITフィルタ
# =========================

def filter_it(items):

    results = []

    for item in items:

        text = item["title"].lower()

        if any(k.lower() in text for k in IT_KEYWORDS):

            results.append(item)

    return results


# =========================
# スコア計算
# =========================

def calculate_scores(items):

    topics = defaultdict(lambda: {"score":0,"sources":set(),"title":""})

    for item in items:

        key = item["title"].lower()

        topics[key]["title"] = item["title"]
        topics[key]["score"] += item["score"]
        topics[key]["sources"].add(item["source"])

    ranked = sorted(
        topics.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked


# =========================
# 表示
# =========================

def shorten_title(title):

    if not CONFIG["SHORT_TITLE"]:
        return title

    max_len = CONFIG["TITLE_MAX_LEN"]

    if len(title) <= max_len:
        return title

    return title[:max_len] + "..."





def show_dashboard(ranked):

    print("\n============================")
    print("ITトレンドダッシュボード")
    print("============================\n")

    for i, item in enumerate(ranked[:CONFIG["DISPLAY_LIMIT"]],1):

        title = shorten_title(item["title"])

        sources = ", ".join(item["sources"])
        score = item["score"]

        # 1行モード
        if CONFIG["ONE_LINE_MODE"]:

            line = f"{i:02d}. {title}"

            if CONFIG["SHOW_SCORE"]:
                line += f" | score:{score}"

            if CONFIG["SHOW_SOURCE"]:
                line += f" | {sources}"

            print(line)

        # 通常モード
        else:

            print(f"{i:02d}. {title}")

            if CONFIG["SHOW_SCORE"]:
                print("   score:", score)

            if CONFIG["SHOW_SOURCE"]:
                print("   sources:", sources)

            print()

# =========================
# メイン
# =========================

def main():

    print("ITトレンド収集中...\n")

    data = []

    data += get_google_trends()
    data += get_hackernews()
    data += get_reddit()
    data += get_qiita()
    data += get_github()

    filtered = filter_it(data)

    ranked = calculate_scores(filtered)

    show_dashboard(ranked)


if __name__ == "__main__":
    main()