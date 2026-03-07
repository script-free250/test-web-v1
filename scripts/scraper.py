"""
STREAMIFY — Larozza Scraper (Full Debug Edition)
كل خطوة بتتطبع بالتفصيل عشان نعرف المشكلة بالضبط
"""

import asyncio, json, re, os, sys, traceback
from urllib.parse import urljoin

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌  playwright مش مثبّت")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
CATEGORY_URL = "https://larozza.online/category.php?cat=ramadan-2026"
BASE_URL     = "https://larozza.online"
OUTPUT_PATH  = os.path.join(os.path.dirname(__file__), "..", "js", "content.js")

# ══════════════════════════════════════════════════════════════
#  LOGGING HELPER
# ══════════════════════════════════════════════════════════════
def log(emoji, msg):
    print(f"{emoji}  {msg}", flush=True)

def sep(title=""):
    print(f"\n{'═'*60}", flush=True)
    if title:
        print(f"  {title}", flush=True)
        print(f"{'═'*60}", flush=True)

# ══════════════════════════════════════════════════════════════
#  BROWSER SETUP
# ══════════════════════════════════════════════════════════════
async def make_browser(pw):
    log("🌐", "تشغيل Chromium...")
    browser = await pw.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ]
    )
    context = await browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
        locale="ar-EG",
        extra_http_headers={"Accept-Language": "ar,en-US;q=0.9,en;q=0.8"}
    )
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.chrome = {runtime: {}};
    """)
    page = await context.new_page()
    log("✅", "Chromium شغّال")
    return browser, page

# ══════════════════════════════════════════════════════════════
#  SAFE NAVIGATE — مع تفاصيل الخطأ
# ══════════════════════════════════════════════════════════════
async def goto(page, url, label=""):
    log("🔗", f"فتح: {url}")
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(1500)

        status = resp.status if resp else "?"
        final  = page.url

        log("📡", f"HTTP Status: {status}  |  Final URL: {final}")

        if status == 403:
            log("⛔", "403 FORBIDDEN — الموقع بيحجب الطلب!")
            return False
        if status == 404:
            log("⚠️", "404 Not Found — الصفحة مش موجودة")
            return False
        if status != 200:
            log("⚠️", f"Status غير متوقع: {status}")
            return False

        # طباعة أول جزء من الصفحة للـ debug
        title = await page.title()
        log("📄", f"عنوان الصفحة: {title}")
        return True

    except Exception as e:
        log("❌", f"خطأ في التنقل: {type(e).__name__}: {e}")
        return False

# ══════════════════════════════════════════════════════════════
#  STEP 1 — قائمة المسلسلات
# ══════════════════════════════════════════════════════════════
async def get_series_list(page):
    sep("STEP 1: جلب قائمة المسلسلات")
    log("🎯", f"الرابط: {CATEGORY_URL}")

    ok = await goto(page, CATEGORY_URL)
    if not ok:
        log("❌", "فشل فتح صفحة الفئة")
        return []

    # ── DEBUG: طباعة HTML كامل ──────────────────────────────
    html = await page.content()
    log("📊", f"حجم HTML: {len(html)} حرف")

    # أول 3000 حرف
    log("🔍", "─── أول 3000 حرف من HTML ───")
    print(html[:3000])
    print("─── نهاية المعاينة ───\n")

    # ── طباعة كل الروابط في الصفحة ──────────────────────────
    all_links = await page.evaluate("""() =>
        Array.from(document.querySelectorAll('a[href]'))
            .map(a => ({href: a.href, text: a.textContent.trim().substring(0,50)}))
            .filter(x => x.href.startsWith('http'))
            .slice(0, 50)
    """)

    sep("كل الروابط في الصفحة (أول 50)")
    for lnk in all_links:
        print(f"  → {lnk['href']}  |  {lnk['text']}")

    # ── طباعة كل الصور ──────────────────────────────────────
    all_imgs = await page.evaluate("""() =>
        Array.from(document.querySelectorAll('img'))
            .map(i => i.src || i.dataset.src || '')
            .filter(Boolean)
            .slice(0, 20)
    """)
    sep("الصور في الصفحة (أول 20)")
    for img in all_imgs:
        print(f"  🖼  {img}")

    # ── محاولة إيجاد كروت المسلسلات ──────────────────────────
    sep("محاولة إيجاد كروت المسلسلات")

    selectors = [
        ('a[href*="view-serie"]',  'روابط view-serie'),
        ('a[href*="serie"]',       'روابط serie'),
        ('a[href*="video"]',       'روابط video'),
        ('.item a',                'كلاس item'),
        ('.col-item a',            'كلاس col-item'),
        ('.video-item a',          'كلاس video-item'),
        ('.movie-item a',          'كلاس movie-item'),
        ('.card a',                'كلاس card'),
        ('.thumb a',               'كلاس thumb'),
        ('article a',              'article'),
        ('.media-box a',           'كلاس media-box'),
        ('.poster a',              'كلاس poster'),
        ('div[class*="item"] a',   'div[class*=item]'),
        ('li[class*="item"] a',    'li[class*=item]'),
        ('a:has(img)',             'أي رابط يحتوي صورة'),
    ]

    series_list = []
    for sel, desc in selectors:
        try:
            els = await page.query_selector_all(sel)
            count = len(els)
            status = "✅" if count > 0 else "❌"
            log(status, f"{desc}: {count} عنصر  [{sel}]")

            if count > 0 and not series_list:
                log("🎯", f"استخدام: {sel}")
                for el in els:
                    href  = await el.get_attribute("href") or ""
                    if not href or href in ("#", "/", "javascript:"):
                        continue
                    full  = urljoin(BASE_URL, href) if not href.startswith("http") else href
                    title = await el.evaluate("""el => {
                        for (const t of ['h1','h2','h3','h4','h5','span','.title','.name']) {
                            const found = el.querySelector(t);
                            if (found) return found.textContent.trim();
                        }
                        return el.textContent.trim().substring(0,80);
                    }""")
                    poster = await el.evaluate("""el => {
                        const img = el.querySelector('img');
                        return img ? (img.dataset.src || img.src || '') : '';
                    }""")
                    if full and "larozza" in full:
                        series_list.append({"title": title.strip(), "url": full, "poster": poster})
        except Exception as e:
            log("⚠️", f"Selector فشل [{sel}]: {e}")

    sep(f"نتيجة STEP 1: {len(series_list)} مسلسل")
    for i, s in enumerate(series_list[:20]):
        log("📺", f"[{i+1}] {s['title'][:50]}  →  {s['url']}")

    return series_list

# ══════════════════════════════════════════════════════════════
#  STEP 2 — حلقات + سرفرات مسلسل واحد
# ══════════════════════════════════════════════════════════════
async def get_series_details(page, info):
    sep(f"مسلسل: {info['title'][:50]}")
    log("🔗", info['url'])

    ok = await goto(page, info['url'])
    if not ok:
        return None

    html = await page.content()
    log("📊", f"حجم HTML: {len(html)}")

    # طباعة الـ HTML
    log("🔍", "─── HTML صفحة المسلسل (أول 2000 حرف) ───")
    print(html[:2000])
    print("───────────────────────────────────────\n")

    # ── روابط الحلقات ──────────────────────────────────────
    sep("بحث عن روابط الحلقات")

    ep_selectors = [
        ('a[href*="play.php"]',    'play.php'),
        ('a[href*="watch"]',        'watch'),
        ('a[href*="episode"]',      'episode'),
        ('a[href*="حلقة"]',        'حلقة'),
        ('[class*="episode"] a',    'class*=episode'),
        ('[class*="eps"] a',        'class*=eps'),
        ('.playlist a',             'playlist'),
        ('.list-ep a',              'list-ep'),
        ('table a',                 'table links'),
    ]

    ep_links = []
    for sel, desc in ep_selectors:
        try:
            els = await page.query_selector_all(sel)
            log("✅" if els else "❌", f"{desc}: {len(els)} رابط  [{sel}]")
            if els and not ep_links:
                for el in els:
                    href = await el.get_attribute("href") or ""
                    text = (await el.inner_text()).strip()
                    if href:
                        full = urljoin(BASE_URL, href)
                        ep_links.append({"url": full, "text": text})
        except Exception as e:
            log("⚠️", f"{sel}: {e}")

    log("📋", f"وُجد {len(ep_links)} حلقة")
    for ep in ep_links[:5]:
        log("  🎬", f"{ep['text'][:30]}  →  {ep['url']}")

    if not ep_links:
        # الصفحة نفسها فيديو؟
        log("🔍", "لا حلقات — جاري البحث عن فيديو في الصفحة...")
        servers = await get_servers(page)
        if servers:
            log("✅", f"وُجد {len(servers)} سرفر مباشرة في الصفحة")
            return build(info, servers[:1][0]["url"], [{"ep":1,"title":"الحلقة 1","titleAr":"الحلقة 1","duration":"—","videoUrl":servers[0]["url"],"servers":servers}])
        return None

    # ── سحب كل حلقة ────────────────────────────────────────
    episodes = []
    for i, ep in enumerate(ep_links[:1]):  # ← حلقة واحدة للتجربة
        ep_num = int(re.search(r'\d+', ep['text'] or str(i+1)).group()) if re.search(r'\d+', ep['text']) else i+1
        log("📺", f"حلقة {ep_num}: {ep['url']}")

        ok = await goto(page, ep['url'])
        if not ok:
            continue

        servers = await get_servers(page)
        log("🖥️", f"  سرفرات: {len(servers)}")
        for s in servers:
            log("  ✅", f"  {s['label']}: {s['url'][:80]}")

        episodes.append({
            "ep": ep_num,
            "title": ep['text'] or f"الحلقة {ep_num}",
            "titleAr": ep['text'] or f"الحلقة {ep_num}",
            "duration": "—",
            "videoUrl": servers[0]["url"] if servers else "",
            "servers": servers,
        })
        await page.wait_for_timeout(1200)

    episodes.sort(key=lambda x: x["ep"])
    return build(info, "", episodes)

# ══════════════════════════════════════════════════════════════
#  السرفرات
# ══════════════════════════════════════════════════════════════
async def get_servers(page):
    sep("بحث عن السرفرات")

    # طباعة iframes
    iframes = await page.evaluate("""() =>
        Array.from(document.querySelectorAll('iframe'))
            .map(f => ({src: f.src, dataSrc: f.dataset?.src || ''}))
    """)
    log("📋", f"iframes: {len(iframes)}")
    for f in iframes:
        log("  🖥️", f"src={f['src'][:80]}  |  data-src={f['dataSrc'][:80]}")

    # طباعة محتوى السكريبتات
    scripts_content = await page.evaluate("""() =>
        Array.from(document.querySelectorAll('script'))
            .map(s => s.textContent || '')
            .filter(t => t.includes('src') || t.includes('file') || t.includes('embed'))
            .map(t => t.substring(0, 300))
    """)
    log("📜", f"سكريبتات تحتوي على src/file/embed: {len(scripts_content)}")
    for i, sc in enumerate(scripts_content[:3]):
        print(f"  Script {i+1}:\n{sc}\n")

    # سحب السرفرات
    servers = await page.evaluate("""() => {
        const results = [];
        const seen = new Set();

        function add(label, url) {
            url = (url || '').trim();
            if (!url || seen.has(url)) return;
            if (url.startsWith('javascript') || url === '#') return;
            if (url.includes('larozza.online') && !url.includes('embed')) return;
            seen.add(url);
            results.push({label: label || 'سرفر', url});
        }

        // iframes
        document.querySelectorAll('iframe').forEach((f,i) => {
            add('سرفر iframe-'+(i+1), f.src || f.dataset?.src || '');
        });

        // أزرار السرفرات
        const btnSels = [
            '[class*="server"]','[class*="source"]','[data-server]',
            '[data-src][href]','[class*="embed"] a','.tab-server',
            '.btn-server','.watch-server','.server-item','.servers a'
        ];
        btnSels.forEach(sel => {
            document.querySelectorAll(sel).forEach((el,i) => {
                const url = el.dataset?.src || el.dataset?.server ||
                            el.dataset?.url || el.href || el.value || '';
                add(el.textContent.trim() || ('سرفر btn-'+i), url);
            });
        });

        // JavaScript
        const patterns = [
            /["'](https?:\/\/[^"']*(?:youtube|ok\.ru|dailymotion|vimeo|streamtape|dood|upstream|sibnet|vidbem|filemoon|mixdrop|streamwish|uqload|fembed|mp4upload|voe\.sx)[^"']*)['"]/gi,
            /["'](https?:\/\/[^"']+\.(?:mp4|m3u8|mkv)(?:\?[^"']*)?)['"]/gi,
        ];
        document.querySelectorAll('script').forEach(s => {
            const code = s.textContent || '';
            patterns.forEach(pat => {
                pat.lastIndex = 0;
                let m;
                while ((m = pat.exec(code)) !== null) {
                    add('سرفر js-'+(results.length+1), m[1]);
                }
            });
        });

        // og:video
        const og = document.querySelector('meta[property="og:video"], meta[property="og:video:url"]');
        if (og?.content) add('og:video', og.content);

        return results;
    }""")

    log("🎯", f"إجمالي السرفرات: {len(servers)}")
    return servers

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def build(info, main_vid, episodes):
    return {
        "title":       info["title"],
        "titleAr":     info["title"],
        "description": "",
        "poster":      info.get("poster",""),
        "backdrop":    info.get("poster",""),
        "year":        2026,
        "rating":      "7.5",
        "genre":       ["دراما","رمضان 2026"],
        "seasons":     1,
        "seasons_data":[{"season":1,"episodes":episodes}],
    }

def gen_js(all_series):
    def j(v): return json.dumps(v, ensure_ascii=False)
    f = all_series[0] if all_series else {}
    fv = f.get("seasons_data",[{}])[0].get("episodes",[{}])[0].get("videoUrl","") if f.get("seasons_data") else ""
    out = [
        "/**",
        f" * STREAMIFY — {len(all_series)} مسلسل — تحديث تلقائي",
        " */",
        "const STREAMIFY_DATA = {",
        "  featured: {",
        f'    id:"featured-1", title:{j(f.get("title",""))}, titleAr:{j(f.get("titleAr",""))},',
        f'    description:"", descriptionAr:"", type:"series",',
        f'    genre:["دراما","رمضان 2026"], year:2026, rating:"7.5", seasons:1,',
        f'    poster:{j(f.get("poster",""))}, backdrop:{j(f.get("poster",""))},',
        f'    videoUrl:{j(fv)}, trailerUrl:{j(fv)}',
        "  },",
        "  movies:[],",
        "  series:[",
    ]
    for i,s in enumerate(all_series):
        last = i==len(all_series)-1
        total = sum(len(sd.get("episodes",[])) for sd in s.get("seasons_data",[]))
        out += [
            "    {",
            f'      id:{j(f"series-{i+1}")}, title:{j(s["title"])}, titleAr:{j(s["titleAr"])},',
            f'      description:{j(s.get("description",""))}, descriptionAr:{j(s.get("description",""))},',
            f'      genre:["دراما","رمضان 2026"], year:{s.get("year",2026)}, rating:{j(s.get("rating","7.5"))},',
            f'      seasons:1, episodes:{total}, poster:{j(s.get("poster",""))}, backdrop:{j(s.get("poster",""))},',
            "      seasons_data:[",
        ]
        for sd in s.get("seasons_data",[]):
            out += ["        {", f'          season:{sd["season"]}, episodes:[']
            for ep in sd.get("episodes",[]):
                out.append(f'            {{ep:{ep["ep"]},title:{j(ep["title"])},titleAr:{j(ep["titleAr"])},duration:{j(ep["duration"])},videoUrl:{j(ep["videoUrl"])},servers:{json.dumps(ep["servers"],ensure_ascii=False)}}},')
            out += ["          ]", "        },"]
        out += ["      ]", f'    }}{"" if last else ","}']
    out += ["  ]","};"]
    return "\n".join(out)

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
async def main():
    sep("STREAMIFY SCRAPER — بدأ العمل 🚀")

    async with async_playwright() as pw:
        try:
            browser, page = await make_browser(pw)
        except Exception as e:
            log("❌", f"فشل تشغيل Chromium: {e}")
            traceback.print_exc()
            sys.exit(1)

        try:
            # STEP 1
            series_list = await get_series_list(page)

            if not series_list:
                sep("❌  STEP 1 فشل — لم يُعثر على مسلسلات")
                log("💡", "راجع HTML المطبوع أعلاه لمعرفة هيكل الصفحة")
                await browser.close()
                sys.exit(1)

            sep(f"✅  STEP 1 نجح — {len(series_list)} مسلسل")

            # STEP 2 — مسلسل واحد للتجربة
            all_series = []
            for idx, s in enumerate(series_list[:1]):
                log("🎬", f"[{idx+1}/1] {s['title'][:50]}")
                details = await get_series_details(page, s)
                if details:
                    all_series.append(details)
                    eps = sum(len(sd["episodes"]) for sd in details["seasons_data"])
                    log("✅", f"نجح — {eps} حلقة")
                else:
                    log("⚠️", "تخطي")

            await browser.close()

            if not all_series:
                sep("❌  لم يُعثر على حلقات في أي مسلسل")
                sys.exit(1)

            # ملخص ما اتسحب
            sep("📊  ملخص ما اتسحب")
            total_eps = total_servers = 0
            for s in all_series:
                eps = s["seasons_data"][0]["episodes"]
                for ep in eps:
                    total_eps += 1
                    total_servers += len(ep.get("servers",[]))
                    log("📺", f"{s['title'][:30]} | ح{ep['ep']} | {len(ep.get('servers',[]))} سرفر | {ep.get('videoUrl','NO VIDEO')[:60]}")

            log("📈", f"الإجمالي: {len(all_series)} مسلسل | {total_eps} حلقة | {total_servers} سرفر")

            # STEP 3 — توليد content.js
            sep("STEP 3: توليد content.js")
            js_content = gen_js(all_series)
            out = os.path.abspath(OUTPUT_PATH)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                f.write(js_content)
            log("✅", f"تم حفظ content.js — {os.path.getsize(out)} bytes")

        except Exception as e:
            sep("❌  خطأ غير متوقع")
            traceback.print_exc()
            await browser.close()
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
