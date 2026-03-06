"""
╔══════════════════════════════════════════════════════════════════╗
║   STREAMIFY — Larozza Auto Scraper                               ║
║   يسحب المسلسلات + الحلقات + السرفرات تلقائياً                  ║
║   ويولّد ملف js/content.js جاهز للموقع                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
import sys
from urllib.parse import urljoin, urlparse

# ══════════════════════════════════════════════════════════════
#  ⚙️  CONFIG — عدّل هنا فقط
# ══════════════════════════════════════════════════════════════

# رابط الفئة المراد سحبها
CATEGORY_URL = "https://larozza.online/category.php?cat=ramadan-2026"

# أقصى عدد صفحات (0 = كل الصفحات)
MAX_PAGES = 0

# أقصى عدد حلقات لكل مسلسل (0 = كل الحلقات)
MAX_EPISODES_PER_SERIES = 0

# وقت الانتظار بين الطلبات (ثانية)
DELAY = 1.2

# مسار ملف الإخراج (نسبي من جذر المشروع)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "js", "content.js")

# ══════════════════════════════════════════════════════════════
#  🌐  HTTP SESSION
# ══════════════════════════════════════════════════════════════
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
})

# ══════════════════════════════════════════════════════════════
#  🔧  HELPERS
# ══════════════════════════════════════════════════════════════

def base_url(url):
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"

def fetch(url, retries=3):
    """Fetch page with retries, return BeautifulSoup or None"""
    for attempt in range(retries):
        try:
            r = SESSION.get(url, timeout=20)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            print(f"  ⚠  HTTP {r.status_code} → {url}")
            if r.status_code == 403:
                print("  ⛔ الموقع يحجب الطلب — جرّب VPN")
                return None
        except Exception as e:
            print(f"  ❌ محاولة {attempt+1}/{retries}: {e}")
            time.sleep(2)
    return None

def txt(el):
    return el.get_text(" ", strip=True) if el else ""

def abs_url(href, base):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return urljoin(base, href)

def best_img(tag):
    """Get image src — handles lazy-loading attributes"""
    for attr in ("data-src", "data-lazy-src", "data-original", "src"):
        v = tag.get(attr, "").strip()
        if v and not v.startswith("data:"):
            return v
    return ""

def extract_number(s):
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else 0

# ══════════════════════════════════════════════════════════════
#  🔍  STEP 1 — سحب قائمة المسلسلات من صفحة الفئة
# ══════════════════════════════════════════════════════════════

def scrape_series_list():
    base = base_url(CATEGORY_URL)
    series_list = []
    page = 1

    while True:
        url = CATEGORY_URL if page == 1 else f"{CATEGORY_URL}&page={page}"
        print(f"\n📄  صفحة {page}: {url}")
        soup = fetch(url)
        if not soup:
            break

        # ── محاولة إيجاد كروت المسلسلات بكل الطرق الممكنة ──
        cards = []

        # الطريقة 1: عناصر article أو div بكلاس يحتوي item/card/thumb/post
        for selector in [
            "article.item", ".item", ".col-item", ".video-item",
            ".series-item", ".category-item", ".post-item",
            "div[class*='item']", "li[class*='item']",
            ".thumb", ".card", "div[class*='card']",
            ".movie-item", ".serie-item", ".media-item",
        ]:
            found = soup.select(selector)
            if found and len(found) > 1:
                cards = found
                break

        # الطريقة 2: روابط تحتوي على صورة ورابط داخلي
        if not cards:
            cards = [
                a for a in soup.find_all("a", href=True)
                if a.find("img")
                and base in abs_url(a["href"], base)
                and a["href"] not in ("/", "#", "")
            ]

        if not cards:
            print("  ✅  لا مزيد من الصفحات")
            break

        added = 0
        for card in cards:
            # الرابط
            link = card if card.name == "a" else card.find("a", href=True)
            if not link:
                continue
            href = abs_url(link.get("href", ""), base)
            if not href or base_url(href) != base:
                continue

            # الاسم
            title_el = (
                card.find(["h1","h2","h3","h4","h5","h6"]) or
                card.find(class_=re.compile(r"title|name|heading", re.I)) or
                card.find("span") or
                link
            )
            title = txt(title_el)
            if not title or len(title) < 2:
                title = href.split("/")[-1].replace("-", " ").strip()

            # الصورة
            img_tag = card.find("img")
            poster = abs_url(best_img(img_tag), base) if img_tag else ""

            # تجنّب التكرار
            if any(s["url"] == href for s in series_list):
                continue

            series_list.append({"title": title, "url": href, "poster": poster})
            added += 1

        print(f"  ✅  {added} مسلسل في هذه الصفحة — الإجمالي: {len(series_list)}")

        if added == 0:
            break

        # التحقق من وجود صفحة تالية
        next_link = (
            soup.select_one("a.next") or
            soup.select_one("li.next > a") or
            soup.select_one(".pagination a[rel='next']") or
            soup.find("a", string=re.compile(r"التالي|Next|»|›", re.I))
        )
        if not next_link:
            break

        page += 1
        if MAX_PAGES and page > MAX_PAGES:
            print(f"  ⏹  وصلت للحد المحدد: {MAX_PAGES} صفحة")
            break

        time.sleep(DELAY)

    return series_list


# ══════════════════════════════════════════════════════════════
#  🎬  STEP 2 — سحب تفاصيل مسلسل واحد (حلقاته + سرفراته)
# ══════════════════════════════════════════════════════════════

def scrape_series_details(info):
    base = base_url(info["url"])
    print(f"  🎬  {info['title'][:55]}")

    soup = fetch(info["url"])
    if not soup:
        return None

    # ── الوصف ──────────────────────────────────────────────────
    desc = ""
    for sel in [
        "[class*='description']", "[class*='story']", "[class*='synopsis']",
        "[class*='plot']", "[class*='overview']", "p.desc", ".about-content"
    ]:
        el = soup.select_one(sel)
        if el and len(txt(el)) > 20:
            desc = txt(el)[:350]
            break

    # ── الصورة (أفضل جودة من og:image) ────────────────────────
    poster = info.get("poster", "")
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        poster = og["content"]

    # ── التقييم ────────────────────────────────────────────────
    rating = "7.0"
    for sel in ["[class*='rating']", "[class*='imdb']", "[class*='score']", "[class*='rate']"]:
        el = soup.select_one(sel)
        if el:
            m = re.search(r'\d+\.?\d*', txt(el))
            if m:
                rating = m.group()
                break

    # ── السنة ──────────────────────────────────────────────────
    year = 2026
    page_text = soup.get_text(" ")
    m = re.search(r'\b(202[0-9]|201[0-9])\b', page_text)
    if m:
        year = int(m.group())

    # ── قائمة الحلقات ──────────────────────────────────────────
    ep_links = []

    # محاولات متعددة لإيجاد روابط الحلقات
    for sel in [
        ".episodes-list a", ".episode-list a", "ul.eps a",
        ".ep-list a", ".playlist a", ".list-ep a",
        "[class*='episode'] a", "[class*='eps'] a",
        "a[href*='episode']", "a[href*='-ep-']", "a[href*='/ep/']",
        "a[href*='watch']", "a[href*='حلقة']",
        "table a[href*='.php']", ".episodios a",
    ]:
        found = soup.select(sel)
        if found:
            ep_links = found
            break

    # إذا ما لقيناش حلقات — الصفحة نفسها هي الفيديو
    if not ep_links:
        servers = extract_servers(soup, base)
        if servers:
            return build_series_obj(info, desc, poster, rating, year, [{
                "ep": 1,
                "title": "الحلقة 1",
                "titleAr": "الحلقة 1",
                "duration": "—",
                "videoUrl": servers[0]["url"],
                "servers": servers,
            }])
        return None

    # ── سحب كل حلقة ────────────────────────────────────────────
    episodes = []
    seen = set()
    limit = MAX_EPISODES_PER_SERIES or len(ep_links)

    for ep_tag in ep_links[:limit]:
        ep_href = abs_url(ep_tag.get("href", ""), base)
        if not ep_href or ep_href in seen or base_url(ep_href) != base:
            continue
        seen.add(ep_href)

        ep_title_raw = txt(ep_tag) or f"الحلقة {len(episodes)+1}"
        ep_num = extract_number(ep_title_raw) or len(episodes) + 1

        # حاول تستخرج رقم الحلقة من العنوان أو الرابط
        num_in_url = re.search(r'(?:ep|episode|حلقة)[_\-]?(\d+)', ep_href, re.I)
        if num_in_url:
            ep_num = int(num_in_url.group(1))

        print(f"      📺  حلقة {ep_num} — {ep_title_raw[:35]}")
        time.sleep(DELAY)

        ep_soup = fetch(ep_href)
        if not ep_soup:
            continue

        servers = extract_servers(ep_soup, base)

        episodes.append({
            "ep":       ep_num,
            "title":    ep_title_raw,
            "titleAr":  ep_title_raw,
            "duration": "—",
            "videoUrl": servers[0]["url"] if servers else "",
            "servers":  servers,
        })

    if not episodes:
        return None

    # ترتيب الحلقات
    episodes.sort(key=lambda x: x["ep"])

    return build_series_obj(info, desc, poster, rating, year, episodes)


def build_series_obj(info, desc, poster, rating, year, episodes):
    return {
        "title":       info["title"],
        "titleAr":     info["title"],
        "description": desc,
        "descriptionAr": desc,
        "poster":      poster,
        "backdrop":    poster,
        "rating":      rating,
        "year":        year,
        "genre":       ["دراما", "رمضان 2026"],
        "seasons": 1,
        "episodes_count": len(episodes),
        "seasons_data": [{
            "season": 1,
            "episodes": episodes,
        }],
    }


# ══════════════════════════════════════════════════════════════
#  🖥️  سحب السرفرات من صفحة الحلقة
# ══════════════════════════════════════════════════════════════

def extract_servers(soup, base):
    """
    يحاول يسحب كل السرفرات المتاحة في الصفحة.
    بيرجع قائمة: [{"label": "سرفر 1", "url": "..."}, ...]
    """
    servers = []
    seen_urls = set()

    def add(label, url):
        url = url.strip()
        if url and url not in seen_urls:
            seen_urls.add(url)
            servers.append({"label": label, "url": url})

    # ── طريقة 1: أزرار السرفرات الصريحة ───────────────────────
    for sel in [
        "[class*='server'] a", "[class*='server'] button",
        "[class*='source'] a", "[data-server]", "[data-src]",
        "[class*='embed'] a", ".btn-server", ".watch-server",
        "ul.list-server li a", ".server-item",
    ]:
        for el in soup.select(sel):
            url = (el.get("data-src") or el.get("data-server") or
                   el.get("href") or el.get("data-url") or "")
            label = txt(el) or f"سرفر {len(servers)+1}"
            if url:
                add(label, abs_url(url, base))

    # ── طريقة 2: iframes مباشرة ────────────────────────────────
    for i, iframe in enumerate(soup.find_all("iframe")):
        url = iframe.get("src") or iframe.get("data-src") or ""
        if url and url.startswith("http"):
            add(f"سرفر {i+1}", url)

    # ── طريقة 3: متغيرات JavaScript ────────────────────────────
    for script in soup.find_all("script"):
        code = script.string or ""
        if not code:
            continue

        # روابط فيديو مباشرة داخل JS
        patterns = [
            # روابط iframe/embed
            r'''(?:src|source|file|url|link|video|embed)\s*[=:]\s*['"]([^'"]+(?:embed|watch|player|stream|video)[^'"]*)['"]\s*''',
            # روابط mp4/m3u8
            r'''['"]([^'"]+\.(?:mp4|m3u8|mkv|webm)(?:\?[^'"]*)?)['"]\s*''',
            # okru / dailymotion / vimeo / streamtape / dood
            r'''['"]([^'"]*(?:ok\.ru|dailymotion|vimeo|streamtape|dood|upstream|sibnet|vidbem|mystream|voe\.sx|filemoon|mixdrop|streamwish|uqload|fembed)[^'"]*)['"]\s*''',
        ]
        for pat in patterns:
            for m in re.finditer(pat, code, re.IGNORECASE):
                url = m.group(1).strip()
                if url.startswith("http") and "larozza" not in url:
                    add(f"سرفر {len(servers)+1}", url)

    # ── طريقة 4: meta og:video ──────────────────────────────────
    og_video = soup.find("meta", property="og:video") or soup.find("meta", {"name":"og:video"})
    if og_video:
        url = og_video.get("content", "")
        if url:
            add("سرفر رئيسي", url)

    return servers


# ══════════════════════════════════════════════════════════════
#  📝  STEP 3 — توليد content.js
# ══════════════════════════════════════════════════════════════

def generate_content_js(all_series):
    """يولّد ملف content.js متوافق مع موقع Streamify"""

    def jstr(v):
        return json.dumps(v, ensure_ascii=False)

    lines = []
    lines += [
        "/**",
        " * ================================================================",
        " *  STREAMIFY — Content Database",
        f" *  ✅ تم التوليد تلقائياً — {len(all_series)} مسلسل",
        " *  🔄 يتحدث تلقائياً عبر GitHub Actions كل يوم",
        " * ================================================================",
        " */",
        "",
        "const STREAMIFY_DATA = {",
        "",
    ]

    # ── Featured ────────────────────────────────────────────────
    f = all_series[0] if all_series else {}
    f_video = ""
    if f.get("seasons_data") and f["seasons_data"][0].get("episodes"):
        f_video = f["seasons_data"][0]["episodes"][0].get("videoUrl", "")

    lines += [
        "  // ══ FEATURED — المميز في الصفحة الرئيسية ══",
        "  featured: {",
        f'    id: "featured-1",',
        f'    title: {jstr(f.get("title",""))},',
        f'    titleAr: {jstr(f.get("titleAr",""))},',
        f'    description: {jstr(f.get("description",""))},',
        f'    descriptionAr: {jstr(f.get("descriptionAr",""))},',
        f'    type: "series",',
        f'    genre: ["دراما", "رمضان 2026"],',
        f'    year: {f.get("year", 2026)},',
        f'    rating: {jstr(f.get("rating","7.0"))},',
        f'    seasons: {f.get("seasons", 1)},',
        f'    poster: {jstr(f.get("poster",""))},',
        f'    backdrop: {jstr(f.get("backdrop",""))},',
        f'    videoUrl: {jstr(f_video)},',
        f'    trailerUrl: {jstr(f_video)}',
        "  },",
        "",
        "  // ══ MOVIES — أضف أفلامك هنا يدوياً ══",
        "  movies: [],",
        "",
        "  // ══ SERIES — مسلسلات رمضان 2026 ══",
        "  series: [",
    ]

    for idx, s in enumerate(all_series):
        sid = f"series-{idx+1}"
        total_eps = sum(
            len(season.get("episodes", []))
            for season in s.get("seasons_data", [])
        )
        is_last = idx == len(all_series) - 1

        lines += [
            "    {",
            f'      id: {jstr(sid)},',
            f'      title: {jstr(s.get("title",""))},',
            f'      titleAr: {jstr(s.get("titleAr",""))},',
            f'      description: {jstr(s.get("description",""))},',
            f'      descriptionAr: {jstr(s.get("descriptionAr",""))},',
            f'      genre: ["دراما", "رمضان 2026"],',
            f'      year: {s.get("year", 2026)},',
            f'      rating: {jstr(s.get("rating","7.0"))},',
            f'      seasons: {s.get("seasons", 1)},',
            f'      episodes: {total_eps},',
            f'      poster: {jstr(s.get("poster",""))},',
            f'      backdrop: {jstr(s.get("backdrop",""))},',
            f'      seasons_data: [',
        ]

        for season in s.get("seasons_data", []):
            lines += [
                "        {",
                f'          season: {season["season"]},',
                "          episodes: [",
            ]
            for ep in season.get("episodes", []):
                servers_js = json.dumps(ep.get("servers", []), ensure_ascii=False)
                lines += [
                    "            {",
                    f'              ep: {ep["ep"]},',
                    f'              title: {jstr(ep.get("title",""))},',
                    f'              titleAr: {jstr(ep.get("titleAr",""))},',
                    f'              duration: {jstr(ep.get("duration","—"))},',
                    f'              videoUrl: {jstr(ep.get("videoUrl",""))},',
                    f'              servers: {servers_js}',
                    "            },",
                ]
            lines += [
                "          ]",
                "        },",
            ]

        lines += [
            "      ]",
            f'    }}{"" if is_last else ","}',
        ]

    lines += [
        "  ]",
        "};",
        "",
        "// ✅ آخر تحديث: تلقائي عبر GitHub Actions",
    ]

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  🚀  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║    STREAMIFY SCRAPER — بدأ العمل 🚀                      ║")
    print(f"║    {CATEGORY_URL[:55]:<55} ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # ── STEP 1: قائمة المسلسلات ───────────────────────────────
    print("\n🔍  STEP 1: جلب قائمة المسلسلات...")
    series_list = scrape_series_list()

    if not series_list:
        print("\n❌  فشل — لم يُعثر على مسلسلات!")
        print("   💡  تأكد من الرابط أو جرّب VPN")
        sys.exit(1)

    print(f"\n✅  وُجد {len(series_list)} مسلسل")
    print("─" * 58)

    # ── STEP 2: تفاصيل + حلقات + سرفرات ──────────────────────
    print("\n🎬  STEP 2: جلب الحلقات والسرفرات لكل مسلسل...")
    all_series = []

    for i, s in enumerate(series_list):
        print(f"\n[{i+1}/{len(series_list)}] {s['title'][:50]}")
        details = scrape_series_details(s)
        if details:
            all_series.append(details)
            eps = sum(len(season["episodes"]) for season in details["seasons_data"])
            print(f"  ✅  {eps} حلقة")
        else:
            print(f"  ⚠️  تخطي (لم تُوجد حلقات)")
        time.sleep(DELAY)

    if not all_series:
        print("\n❌  لم يُعثر على أي حلقات!")
        sys.exit(1)

    print(f"\n✅  اكتمل: {len(all_series)} مسلسل")
    print("─" * 58)

    # ── STEP 3: توليد content.js ──────────────────────────────
    print("\n📝  STEP 3: توليد js/content.js ...")
    content_js = generate_content_js(all_series)

    out_path = os.path.abspath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content_js)

    total_eps = sum(
        len(season["episodes"])
        for s in all_series
        for season in s["seasons_data"]
    )

    print(f"\n╔══════════════════════════════════════════════════════════╗")
    print(f"║  ✅  تم بنجاح!                                            ║")
    print(f"║  📺  {len(all_series)} مسلسل — {total_eps} حلقة إجمالاً              ║")
    print(f"║  📄  {os.path.basename(out_path):<50} ║")
    print(f"╚══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
