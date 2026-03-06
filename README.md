# 🎬 Streamify — دليل الاستخدام الكامل

موقع استريمينج احترافي لمشاهدة الأفلام والمسلسلات، مبني بـ HTML/CSS/JS خالص.

---

## 🗂️ هيكل الملفات

```
streamify/
├── index.html              ← الصفحة الرئيسية
├── browse.html             ← صفحة تصفح المحتوى
├── player.html             ← صفحة مشاهدة الفيديو
├── css/
│   └── style.css           ← كل التصميم
├── js/
│   ├── content.js          ← 📌 هنا تضيف أفلامك ومسلسلاتك
│   └── app.js              ← منطق التطبيق (لا تعدله)
└── .github/
    └── workflows/
        └── deploy.yml      ← رفع تلقائي على GitHub Pages
```

---

## ✅ خطوات رفع الموقع على GitHub Pages

### 1. إنشاء الـ Repository

- ادخل على [github.com](https://github.com) وأنشئ Repository جديد
- سمّيه مثلاً: `streamify`
- اختر **Public**

### 2. رفع الملفات

```bash
git init
git add .
git commit -m "🎬 Initial Streamify deploy"
git branch -M main
git remote add origin https://github.com/اسمك/streamify.git
git push -u origin main
```

### 3. تفعيل GitHub Pages

- اذهب إلى **Settings → Pages**
- في Source اختر: **GitHub Actions**
- احفظ

### 4. اضغط على الرابط 🎉

بعد دقيقة هيظهرلك رابط الموقع:
```
https://اسمك.github.io/streamify/
```

---

## 📹 كيف تضيف أفلامك ومسلسلاتك؟ (بدون تحميل أو رفع!)

### الطريقة الأولى: YouTube (الأسهل ✅)

1. ارفع الفيديو على YouTube
2. اضغط **Share → Copy Link**
3. الرابط هيكون زي: `https://www.youtube.com/watch?v=ABC123`
4. افتح `js/content.js` وحط الـ ID في `videoUrl`:

```js
videoUrl: "https://www.youtube.com/embed/ABC123"
//                                         ^^^^^^
//                              ده الـ ID اللي بعد v=
```

> 💡 لو مش عايز الناس يشوفوه على YouTube، اختار **Unlisted** (غير مدرج)

---

### الطريقة الثانية: Google Drive (للملفات الكبيرة ✅)

1. ارفع الفيديو على Google Drive
2. كليك يمين → **Share** → **Anyone with the link**
3. الرابط هيكون: `https://drive.google.com/file/d/XXXXXXXXXXX/view`
4. في `content.js` حط:

```js
videoUrl: "https://drive.google.com/file/d/XXXXXXXXXXX/preview"
//                                          ^^^^^^^^^^^
//                                    ده الـ ID من الرابط
```

---

### الطريقة الثالثة: رابط مباشر (MP4)

لو عندك رابط MP4 مباشر من أي موقع:

```js
videoUrl: "https://example.com/video.mp4"
```

---

## ➕ إضافة فيلم جديد

افتح `js/content.js` وأضف في قسم `movies`:

```js
{
  id: "movie-7",                          // ← رقم مميز (غير عن الباقيين)
  title: "My Movie",                      // ← الاسم بالإنجليزي
  titleAr: "فيلمي الجديد",               // ← الاسم بالعربي
  description: "English description",
  descriptionAr: "وصف الفيلم بالعربي",
  genre: ["Action", "Drama"],             // ← التصنيفات
  year: 2024,
  rating: "8.5",
  duration: "120 min",
  poster: "https://رابط_صورة_البوستر.jpg",  // ← صورة الغلاف
  backdrop: "https://رابط_صورة_خلفية.jpg",  // ← صورة الخلفية (اختياري)
  videoUrl: "https://www.youtube.com/embed/VIDEO_ID",  // ← رابط الفيديو
},
```

> 💡 لصور البوستر: استخدم [TMDB](https://www.themoviedb.org/) وانسخ رابط الصورة

---

## ➕ إضافة مسلسل جديد

```js
{
  id: "series-7",
  title: "My Series",
  titleAr: "مسلسلي الجديد",
  description: "Description",
  descriptionAr: "الوصف",
  genre: ["Drama", "Action"],
  year: 2024,
  rating: "9.0",
  seasons: 1,
  episodes: 5,
  poster: "https://رابط_الصورة.jpg",
  backdrop: "https://رابط_الخلفية.jpg",
  seasons_data: [
    {
      season: 1,
      episodes: [
        { ep: 1, title: "Episode 1", titleAr: "الحلقة الأولى", duration: "45 min", videoUrl: "https://www.youtube.com/embed/VIDEO_ID_1" },
        { ep: 2, title: "Episode 2", titleAr: "الحلقة الثانية", duration: "47 min", videoUrl: "https://www.youtube.com/embed/VIDEO_ID_2" },
        // ... باقي الحلقات
      ]
    }
  ]
},
```

---

## 🚀 بعد أي تعديل — كيف تحدّث الموقع؟

```bash
git add .
git commit -m "✅ إضافة [اسم الفيلم/المسلسل]"
git push
```

GitHub Actions هيحدّث الموقع تلقائياً خلال دقيقة! 🎉

---

## 🛠️ تخصيص إضافي

| ما تريد تغييره | أين تغيره |
|---|---|
| اسم الموقع | `css/style.css` → `.logo-text` |
| ألوان الموقع | `css/style.css` → `:root` (CSS Variables) |
| المحتوى المميز في الـ Banner | `js/content.js` → `featured` |
| إضافة تصنيفات جديدة | `browse.html` → `.filter-bar` |

---

## 📱 الموقع Responsive؟

نعم! يعمل على:
- 💻 كمبيوتر
- 📱 موبايل
- 📟 تابلت

---

*صُمّم بـ ❤️ — Streamify*
