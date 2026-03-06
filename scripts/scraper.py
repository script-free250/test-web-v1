"""
╔══════════════════════════════════════════════════════════════════╗
║   STREAMIFY — Larozza Scraper (Playwright Edition)               ║
║   بيشغّل متصفح Chromium حقيقي لتجاوز حماية Cloudflare           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import json
import re
import os
import sys
import time
from urllib.parse import urljoin, urlparse, parse_qs

try:
    from playwright.async_api import async_playwright, TimeoutError as PWTimeout
except ImportError:
    print("❌ playwright غير مثبّت — شغّل: pip install playwright && playwright install chromium")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════
#  ⚙️  CONFIG
# ══════════════════════════════════════════════════════════════

CATEGORY_URL     = "https://larozza.online/category.php?cat=ramadan-2026"
BASE_URL         = "https://larozza.online"
OUTPUT_PATH      = os.path.join(os.path.dirname(__file__), "..", "js", "content.js")
MAX_PAGES        = 0        # 0 = كل الصفحات
MAX_EPS_PER_SHOW = 0        # 0 = كل الحلقات
PAGE_DELAY       = 1500     # ms بين الصفحات
NAV_TIMEOUT      = 30000    # ms

# ══════════════════════════════════════════════════════════════
#  🔧  HELPERS
# ══════════════════════════════════════════════════════════════

def clean(s):
    return re.sub(r'\s+', ' ', str(s or "")).strip()

def extract_num(s):
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else 0

async def goto(page, url, wait="domcontentloaded"):
    """Navigate with retry"""
    for attempt in range(3):
        try:
            await page.goto(url, wait_until=wait, timeout=NAV_TIMEOUT)
            await page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"    ⚠  محاولة {attempt+1}/3: {e}")
            await page.wait_for_timeout(2000)
    return False

# ══════════════════════════════════════════════════════════════
#  🔍  STEP 1 — قائمة المسلسلات من صفحة الفئة
# ══════════════════════════════════════════════════════════════

async def scrape_series_list(page):
    print(f"\n🔍  جلب قائمة المسلسلات من:")
    print(f"    {CATEGORY_URL}\n")

    series_list = []
    page_num = 1

    while True:
        url = CATEGORY_URL if page_num == 1 else f"{CATEGORY_URL}&page={page_num}"
        print(f"  📄  صفحة {page_num}: {url}")

        ok = await goto(page, url)
        if not ok:
            print("  ❌  فشل تحميل الصفحة")
            break

        # ── DEBUG: طباعة هيكل الصفحة ──────────────────────────
        if page_num == 1:
            html_snippet = await page.evaluate("document.body.innerHTML.substring(0, 2000)")
            print(f"\n  🔎  DEBUG — أول 2000 حرف من الصفحة:\n{html_snippet}\n")

        # ── إيجاد كروت المسلسلات ──────────────────────────────
        # جرّب كل الـ selectors الممكنة
        selectors_to_try = [
            # روابط تحتوي view-serie في الـ href
            'a[href*="view-serie"]',
            'a[href*="serie"]',
            # كروت شائعة
            ".item a", ".col-item a", ".video-item a",
            ".category-item a", ".media-item a",
            # أي رابط يحتوي صورة
            "article a", ".card a", ".thumb a",
            # fallback: كل الروابط الداخلية
            f'a[href^="{BASE_URL}"]',
            "a[href^='/']",
        ]

        cards = []
        used_selector = ""
        for sel in selectors_to_try:
            elements = await page.query_selector_all(sel)
            if elements:
                cards = elements
                used_selector = sel
                print(f"  ✅  وجد {len(elements)} عنصر بـ selector: {sel}")
                break

        if not cards:
            # طباعة كل الروابط الموجودة للـ debug
            all_links = await page.evaluate("""
                Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(h => h.includes('larozza'))
                    .slice(0, 30)
            """)
            print(f"  🔎  كل الروابط الموجودة:\n    " + "\n    ".join(all_links))
            break

        added = 0
        for el in cards:
            href = await el.get_attribute("href") or ""
            if not href or href in ("#", "/"):
                continue

            full_url = urljoin(BASE_URL, href)

            # تجاهل الروابط غير المتعلقة بالمسلسلات
            skip_patterns = ["category.php", "home", "login", "register", "search", "user.php", "newvideos"]
            if any(p in full_url for p in skip_patterns):
                continue

            if any(s["url"] == full_url for s in series_list):
                continue

            # اسم المسلسل
            title = await el.evaluate("""el => {
                const h = el.querySelector('h1,h2,h3,h4,h5,span.title,span.name,.title,.name');
                if (h) return h.textContent.trim();
                const img = el.querySelector('img');
                if (img) return img.alt || img.title || '';
                return el.textContent.trim().substring(0, 80);
            }""")
            title = clean(title)
            if not title or len(title) < 2:
                title = href.split("/")[-1].split("?")[0].replace("-", " ") or "مسلسل"

            # الصورة
            poster = await el.evaluate("""el => {
                const img = el.querySelector('img');
                if (!img) return '';
                return img.dataset.src || img.dataset.lazySrc || img.src || '';
            }""")
            poster = poster or ""

            series_list.append({"title": title, "url": full_url, "poster": poster})
            added += 1

        print(f"  📊  أُضيف {added} — الإجمالي: {len(series_list)}")

        if added == 0:
            break

        # التحقق من صفحة تالية
        next_btn = await page.query_selector(
            "a.next, li.next > a, .pagination a[rel='next'], a:has-text('التالي'), a:has-text('Next')"
        )
        if not next_btn:
            print("  ✅  انتهت الصفحات")
            break

        page_num += 1
        if MAX_PAGES and page_num > MAX_PAGES:
            break

        await page.wait_for_timeout(PAGE_DELAY)

    return series_list


# ══════════════════════════════════════════════════════════════
#  🎬  STEP 2 — تفاصيل المسلسل + حلقاته
# ══════════════════════════════════════════════════════════════

async def scrape_series_details(page, info):
    print(f"  🎬  {info['title'][:55]}")

    ok = await goto(page, info["url"])
    if not ok:
        return None

    # ── الوصف ──────────────────────────────────────────────────
    desc = await page.evaluate("""() => {
        const selectors = ['.description','.story','.synopsis','.plot','.overview','.about','.info-desc','p.desc'];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el && el.textContent.trim().length > 20)
                return el.textContent.trim().substring(0, 350);
        }
        return '';
    }""")

    # ── الصورة (أفضل جودة) ─────────────────────────────────────
    poster = await page.evaluate("""() => {
        const og = document.querySelector('meta[property="og:image"]');
        if (og) return og.content;
        const img = document.querySelector('.poster img, .serie-poster img, .cover img');
        if (img) return img.dataset.src || img.src || '';
        return '';
    }""") or info.get("poster", "")

    # ── السنة والتقييم ─────────────────────────────────────────
    year_rating = await page.evaluate("""() => {
        const text = document.body.innerText;
        const yearMatch = text.match(/\\b(202[0-9]|201[0-9])\\b/);
        const ratingMatch = text.match(/(?:IMDB|تقييم)[^\\d]*(\\d+\\.?\\d*)/i) 
                         || text.match(/\\b(\\d\\.\\d)\\b.*(?:IMDB|rating)/i);
        return {
            year: yearMatch ? parseInt(yearMatch[0]) : 2026,
            rating: ratingMatch ? ratingMatch[1] : '7.5'
        };
    }""")

    # ── قائمة الحلقات ──────────────────────────────────────────
    ep_links = await page.evaluate(f"""() => {{
        const base = '{BASE_URL}';
        const links = [];
        const seen = new Set();

        // روابط الحلقات — أولوية للروابط التي تحتوي video.php
        const candidates = Array.from(document.querySelectorAll('a[href]'));
        for (const a of candidates) {{
            const href = a.href || '';
            if (!href || seen.has(href)) continue;
            if (href.includes('video.php') || href.includes('/watch/') || href.includes('/episode/')) {{
                seen.add(href);
                const txt = a.textContent.trim();
                links.push({{ url: href, text: txt }});
            }}
        }}

        // إذا مافيش video.php، جرّب روابط عامة
        if (links.length === 0) {{
            for (const a of candidates) {{
                const href = a.href || '';
                if (!href || seen.has(href)) continue;
                if (href.includes(base) && !href.includes('category') && 
                    !href.includes('view-serie') && href !== window.location.href) {{
                    seen.add(href);
                    links.push({{ url: href, text: a.textContent.trim() }});
                }}
            }}
        }}

        return links.slice(0, {MAX_EPS_PER_SHOW or 60});
    }}""")

    # إذا ما لقيناش حلقات — الصفحة نفسها فيديو
    if not ep_links:
        servers = await extract_servers(page)
        if servers:
            return build_obj(info, clean(desc), poster, year_rating, [{
                "ep": 1, "title": "الحلقة 1", "titleAr": "الحلقة 1",
                "duration": "—", "videoUrl": servers[0]["url"], "servers": servers,
            }])
        return None

    # ── سحب كل حلقة ────────────────────────────────────────────
    episodes = []
    seen_eps = set()

    for ep_info in ep_links:
        ep_url = ep_info["url"]
        if ep_url in seen_eps:
            continue
        seen_eps.add(ep_url)

        ep_text = clean(ep_info["text"]) or f"الحلقة {len(episodes)+1}"
        ep_num = extract_num(ep_text) or len(episodes) + 1

        # رقم الحلقة من الرابط
        vid_match = re.search(r'vid=([a-f0-9]+)', ep_url)
        ep_in_url = re.search(r'(?:ep|episode|حلقة)[_\-]?(\d+)', ep_url, re.I)
        if ep_in_url:
            ep_num = int(ep_in_url.group(1))

        print(f"      📺  ح{ep_num} — {ep_text[:35]}")

        ok = await goto(page, ep_url)
        if not ok:
            continue

        servers = await extract_servers(page)

        episodes.append({
            "ep":       ep_num,
            "title":    ep_text,
            "titleAr":  ep_text,
            "duration": "—",
            "videoUrl": servers[0]["url"] if servers else "",
            "servers":  servers,
        })

        await page.wait_for_timeout(PAGE_DELAY)

    if not episodes:
        return None

    episodes.sort(key=lambda x: x["ep"])
    return build_obj(info, clean(desc), poster, year_rating, episodes)


# ══════════════════════════════════════════════════════════════
#  🖥️  سحب السرفرات من صفحة الحلقة
# ══════════════════════════════════════════════════════════════

async def extract_servers(page):
    servers = []

    raw = await page.evaluate("""() => {
        const results = [];
        const seen = new Set();

        function add(label, url) {
            if (!url || seen.has(url)) return;
            // تجاهل الروابط الداخلية
            if (url.includes('larozza.online') && !url.includes('embed')) return;
            seen.add(url);
            results.push({ label: label || 'سرفر', url: url });
        }

        // 1. أزرار السرفرات الصريحة
        const serverBtns = document.querySelectorAll(
            '[class*="server"] a, [class*="source"] a, [data-server], ' +
            '[data-src], .btn-server, .watch-server, .server-item, ' +
            '.embed-item a, [class*="embed"] a, .tab-server, ' +
            'ul.list-server li a, .servers a'
        );
        serverBtns.forEach((el, i) => {
            const url = el.dataset?.src || el.dataset?.server || 
                        el.dataset?.url || el.href || '';
            const lbl = el.textContent.trim() || `سرفر ${i+1}`;
            add(lbl, url);
        });

        // 2. iframes مباشرة
        document.querySelectorAll('iframe').forEach((f, i) => {
            const url = f.src || f.dataset?.src || '';
            add(`سرفر ${i+1}`, url);
        });

        // 3. JavaScript variables — بحث في كل السكريبتات
        const videoPatterns = [
            /(?:src|file|url|source|embed|video)['":\\s]+['"]([^'"]+(?:youtube|ok\\.ru|dailymotion|vimeo|streamtape|dood|upstream|sibnet|vidbem|mystream|voe\\.sx|filemoon|mixdrop|streamwish|uqload|fembed|mp4)[^'"]*)['"]/gi,
            /['"]([^'"]+\\.(?:mp4|m3u8|mkv)(?:\\?[^'"]*)?)['"]/gi,
        ];
        document.querySelectorAll('script').forEach(s => {
            const code = s.textContent || '';
            videoPatterns.forEach(pat => {
                pat.lastIndex = 0;
                let m;
                while ((m = pat.exec(code)) !== null) {
                    add(`سرفر ${results.length+1}`, m[1]);
                }
            });
        });

        // 4. og:video
        const ogVid = document.querySelector('meta[property="og:video"], meta[property="og:video:url"]');
        if (ogVid?.content) add('سرفر رئيسي', ogVid.content);

        return results;
    }""")

    return raw or []


# ══════════════════════════════════════════════════════════════
#  🏗️  بناء كائن المسلسل
# ══════════════════════════════════════════════════════════════

def build_obj(info, desc, poster, yr, episodes):
    return {
        "title":          info["title"],
        "titleAr":        info["title"],
        "description":    desc,
        "descriptionAr":  desc,
        "poster":         poster,
        "backdrop":       poster,
        "year":           yr.get("year", 2026),
        "rating":         yr.get("rating", "7.5"),
        "genre":          ["دراما", "رمضان 2026"],
        "seasons":        1,
        "seasons_data":   [{"season": 1, "episodes": episodes}],
    }


# ══════════════════════════════════════════════════════════════
#  📝  STEP 3 — توليد content.js
# ══════════════════════════════════════════════════════════════

def generate_content_js(all_series):
    def js(v):
        return json.dumps(v, ensure_ascii=False)

    lines = [
        "/**",
        " * ================================================================",
        " *  STREAMIFY — Content Database",
        f" *  ✅ {len(all_series)} مسلسل — تحديث تلقائي عبر GitHub Actions",
        " * ================================================================",
        " */",
        "",
        "const STREAMIFY_DATA = {",
        "",
    ]

    # Featured
    f = all_series[0] if all_series else {}
    f_vid = ""
    if f.get("seasons_data") and f["seasons_data"][0].get("episodes"):
        f_vid = f["seasons_data"][0]["episodes"][0].get("videoUrl", "")

    lines += [
        "  featured: {",
        f'    id: "featured-1",',
        f'    title: {js(f.get("title",""))},',
        f'    titleAr: {js(f.get("titleAr",""))},',
        f'    description: {js(f.get("description",""))},',
        f'    descriptionAr: {js(f.get("descriptionAr",""))},',
        f'    type: "series",',
        f'    genre: ["دراما","رمضان 2026"],',
        f'    year: {f.get("year",2026)},',
        f'    rating: {js(f.get("rating","7.5"))},',
        f'    seasons: 1,',
        f'    poster: {js(f.get("poster",""))},',
        f'    backdrop: {js(f.get("backdrop",""))},',
        f'    videoUrl: {js(f_vid)},',
        f'    trailerUrl: {js(f_vid)}',
        "  },",
        "",
        "  movies: [],",
        "",
        "  series: [",
    ]

    for i, s in enumerate(all_series):
        sid = f"series-{i+1}"
        total = sum(len(sd.get("episodes", [])) for sd in s.get("seasons_data", []))
        last = i == len(all_series) - 1

        lines += [
            "    {",
            f'      id: {js(sid)},',
            f'      title: {js(s.get("title",""))},',
            f'      titleAr: {js(s.get("titleAr",""))},',
            f'      description: {js(s.get("description",""))},',
            f'      descriptionAr: {js(s.get("descriptionAr",""))},',
            f'      genre: ["دراما","رمضان 2026"],',
            f'      year: {s.get("year",2026)},',
            f'      rating: {js(s.get("rating","7.5"))},',
            f'      seasons: 1,',
            f'      episodes: {total},',
            f'      poster: {js(s.get("poster",""))},',
            f'      backdrop: {js(s.get("backdrop",""))},',
            f'      seasons_data: [',
        ]

        for sd in s.get("seasons_data", []):
            lines += ["        {", f'          season: {sd["season"]},', "          episodes: ["]
            for ep in sd.get("episodes", []):
                lines += [
                    "            {",
                    f'              ep: {ep["ep"]},',
                    f'              title: {js(ep.get("title",""))},',
                    f'              titleAr: {js(ep.get("titleAr",""))},',
                    f'              duration: {js(ep.get("duration","—"))},',
                    f'              videoUrl: {js(ep.get("videoUrl",""))},',
                    f'              servers: {json.dumps(ep.get("servers",[]), ensure_ascii=False)}',
                    "            },",
                ]
            lines += ["          ]", "        },"]

        lines += ["      ]", f'    }}{"" if last else ","}']

    lines += ["  ]", "};", "", "// 🤖 تم التحديث تلقائياً"]
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
#  🚀  MAIN
# ══════════════════════════════════════════════════════════════

async def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║    STREAMIFY SCRAPER (Playwright) — بدأ 🚀               ║")
    print("╚══════════════════════════════════════════════════════════╝")

    async with async_playwright() as pw:
        # تشغيل Chromium بـ stealth mode
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ]
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="ar-EG",
            extra_http_headers={
                "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
                "Referer": BASE_URL,
            }
        )

        # إخفاء علامات الـ automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ar','en'] });
            window.chrome = { runtime: {} };
        """)

        page = await context.new_page()

        # ── STEP 1 ──────────────────────────────────────────────
        print("\n🔍  STEP 1: جلب قائمة المسلسلات...")
        series_list = await scrape_series_list(page)

        if not series_list:
            print("\n❌  لم يُعثر على مسلسلات — تحقق من DEBUG أعلاه")
            await browser.close()
            sys.exit(1)

        print(f"\n✅  وُجد {len(series_list)} مسلسل")

        # ── STEP 2 ──────────────────────────────────────────────
        print("\n🎬  STEP 2: جلب الحلقات والسرفرات...")
        all_series = []

        for idx, s in enumerate(series_list):
            print(f"\n[{idx+1}/{len(series_list)}] {s['title'][:50]}")
            details = await scrape_series_details(page, s)
            if details:
                eps = sum(len(sd["episodes"]) for sd in details["seasons_data"])
                print(f"  ✅  {eps} حلقة")
                all_series.append(details)
            else:
                print(f"  ⚠️  تخطي (لا حلقات)")

            await page.wait_for_timeout(PAGE_DELAY)

        await browser.close()

        if not all_series:
            print("\n❌  لم يُعثر على أي حلقات!")
            sys.exit(1)

        # ── STEP 3 ──────────────────────────────────────────────
        print(f"\n📝  STEP 3: توليد content.js ({len(all_series)} مسلسل)...")
        js_content = generate_content_js(all_series)

        out = os.path.abspath(OUTPUT_PATH)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(js_content)

        total_eps = sum(
            len(sd["episodes"])
            for s in all_series
            for sd in s["seasons_data"]
        )

        print(f"\n╔══════════════════════════════════════════════════════════╗")
        print(f"║  🎉  تم بنجاح!                                            ║")
        print(f"║  📺  {len(all_series)} مسلسل — {total_eps} حلقة                         ║")
        print(f"╚══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    asyncio.run(main())
