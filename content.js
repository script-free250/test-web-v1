/**
 * ============================================================
 *  STREAMIFY — Content Database
 * ============================================================
 *  📌 HOW TO ADD YOUR CONTENT (بالعربي في الأسفل):
 *
 *  YOUTUBE VIDEO:
 *    videoUrl: "https://www.youtube.com/embed/VIDEO_ID"
 *    (Replace VIDEO_ID with the ID after ?v= in the YouTube link)
 *
 *  GOOGLE DRIVE VIDEO:
 *    videoUrl: "https://drive.google.com/file/d/FILE_ID/preview"
 *    (Replace FILE_ID with the ID from your Google Drive share link)
 *
 *  ─────────────────────────────────────────────────────────
 *  📌 طريقة إضافة محتواك (بسيطة جداً):
 *
 *  1. ارفع الفيديو على YouTube كـ "Unlisted" (غير مدرج)
 *     أو على Google Drive وشاركه كـ "Anyone with the link"
 *
 *  2. انسخ الـ ID من الرابط وحطه في videoUrl زي المثال فوق
 *
 *  3. احفظ الملف وادفعه على GitHub — خلاص! 🎉
 * ============================================================
 */

const STREAMIFY_DATA = {

  // ═══════════════════════════════════════════════
  //  🎬 FEATURED HERO — الـ Banner الرئيسي
  // ═══════════════════════════════════════════════
  featured: {
    id: "featured-1",
    title: "Dune: Part Two",
    titleAr: "كثيب الجزء الثاني",
    description: "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
    descriptionAr: "بول أتريدس يتحد مع شعب الفريمن ويسعى للانتقام من المتآمرين الذين دمروا عائلته في ملحمة خيال علمي لا تُنسى.",
    type: "movie",
    genre: ["Sci-Fi", "Adventure", "Drama"],
    year: 2024,
    rating: "8.5",
    duration: "166 min",
    poster: "https://image.tmdb.org/t/p/original/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
    backdrop: "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg",
    videoUrl: "https://www.youtube.com/embed/Way9Dexny3w", // ← Replace with your video
    trailerUrl: "https://www.youtube.com/embed/Way9Dexny3w"
  },

  // ═══════════════════════════════════════════════
  //  🎥 MOVIES — الأفلام
  // ═══════════════════════════════════════════════
  movies: [
    {
      id: "movie-1",
      title: "Oppenheimer",
      titleAr: "أوبنهايمر",
      description: "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
      descriptionAr: "قصة العالم الأمريكي روبرت أوبنهايمر ودوره في تطوير القنبلة الذرية.",
      genre: ["Drama", "History", "Thriller"],
      year: 2023,
      rating: "8.3",
      duration: "180 min",
      poster: "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg",
      videoUrl: "https://www.youtube.com/embed/uYPbbksJxIg", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/uYPbbksJxIg"
    },
    {
      id: "movie-2",
      title: "Inception",
      titleAr: "إنسبشن",
      description: "A thief who steals corporate secrets through the use of dream-sharing technology.",
      descriptionAr: "لص يسرق أسرار الشركات عن طريق تقنية مشاركة الأحلام ويُكلَّف بمهمة عكسية.",
      genre: ["Action", "Sci-Fi", "Thriller"],
      year: 2010,
      rating: "8.8",
      duration: "148 min",
      poster: "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
      videoUrl: "https://www.youtube.com/embed/YoHD9XEInc0", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/YoHD9XEInc0"
    },
    {
      id: "movie-3",
      title: "Interstellar",
      titleAr: "إنترستيلار",
      description: "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
      descriptionAr: "فريق من المستكشفين يسافر عبر ثقب دودي في الفضاء لإنقاذ البشرية.",
      genre: ["Sci-Fi", "Drama", "Adventure"],
      year: 2014,
      rating: "8.7",
      duration: "169 min",
      poster: "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/pbrkL804wWAxNv9d4LPm7AwMpzD.jpg",
      videoUrl: "https://www.youtube.com/embed/zSWdZVtXT7E", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/zSWdZVtXT7E"
    },
    {
      id: "movie-4",
      title: "The Dark Knight",
      titleAr: "فارس الظلام",
      description: "Batman faces the Joker, a criminal mastermind who plunges Gotham City into chaos.",
      descriptionAr: "باتمان يواجه الجوكر المجرم العبقري الذي يغرق مدينة غوثام في الفوضى.",
      genre: ["Action", "Crime", "Drama"],
      year: 2008,
      rating: "9.0",
      duration: "152 min",
      poster: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/nMKdUUepR0i5zn0y1T4CejMItX3.jpg",
      videoUrl: "https://www.youtube.com/embed/EXeTwQWrcwY", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/EXeTwQWrcwY"
    },
    {
      id: "movie-5",
      title: "Avatar: The Way of Water",
      titleAr: "أفاتار: طريق الماء",
      description: "Jake Sully and Ney'tiri have formed a family and are doing everything to stay together.",
      descriptionAr: "جيك سالي ونيتيري أسسا عائلة ويكافحان للبقاء معاً على كوكب باندورا.",
      genre: ["Action", "Sci-Fi", "Adventure"],
      year: 2022,
      rating: "7.6",
      duration: "192 min",
      poster: "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/s16H6tpK2utvwpatzNuqtSCMQV8.jpg",
      videoUrl: "https://www.youtube.com/embed/d9MyW72ELq0", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/d9MyW72ELq0"
    },
    {
      id: "movie-6",
      title: "Gladiator II",
      titleAr: "المجلادياتور 2",
      description: "Years after witnessing the death of Maximus, Lucius is forced to enter the Colosseum after his home is conquered.",
      descriptionAr: "بعد سنوات من مشاهدته لموت ماكسيموس، يُجبر لوسيوس على دخول الكولوسيوم.",
      genre: ["Action", "Drama", "History"],
      year: 2024,
      rating: "7.2",
      duration: "148 min",
      poster: "https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/euYIwmwkmz95mnXvBnEd0fFMZJa.jpg",
      videoUrl: "https://www.youtube.com/embed/1VIZ89FEjYI", // ← Replace with your video
      trailerUrl: "https://www.youtube.com/embed/1VIZ89FEjYI"
    }
  ],

  // ═══════════════════════════════════════════════
  //  📺 SERIES — المسلسلات
  // ═══════════════════════════════════════════════
  series: [
    {
      id: "series-1",
      title: "Breaking Bad",
      titleAr: "بريكينغ باد",
      description: "A high school chemistry teacher turned methamphetamine manufacturer partners with a former student.",
      descriptionAr: "معلم كيمياء يتحول إلى صانع مخدرات بعد تشخيصه بالسرطان في مسلسل درامي استثنائي.",
      genre: ["Crime", "Drama", "Thriller"],
      year: 2008,
      rating: "9.5",
      seasons: 5,
      episodes: 62,
      poster: "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
      // ← كل موسم فيه قائمة حلقات
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "Pilot", titleAr: "البداية", duration: "58 min", videoUrl: "https://www.youtube.com/embed/HhesaQXLuRY" },
            { ep: 2, title: "Cat's in the Bag", titleAr: "القطة في الكيس", duration: "48 min", videoUrl: "https://www.youtube.com/embed/HhesaQXLuRY" },
            { ep: 3, title: "And the Bag's in the River", titleAr: "والكيس في النهر", duration: "48 min", videoUrl: "https://www.youtube.com/embed/HhesaQXLuRY" }
          ]
        },
        {
          season: 2,
          episodes: [
            { ep: 1, title: "Seven Thirty-Seven", titleAr: "سبعمائة وسبعة وثلاثون", duration: "47 min", videoUrl: "https://www.youtube.com/embed/HhesaQXLuRY" },
            { ep: 2, title: "Grilled", titleAr: "مشوي", duration: "46 min", videoUrl: "https://www.youtube.com/embed/HhesaQXLuRY" }
          ]
        }
      ]
    },
    {
      id: "series-2",
      title: "Game of Thrones",
      titleAr: "لعبة العروش",
      description: "Nine noble families fight for control over the mythical lands of Westeros.",
      descriptionAr: "تسع عائلات نبيلة تتصارع على السيطرة على أراضي ويستيروس الأسطورية.",
      genre: ["Fantasy", "Drama", "Adventure"],
      year: 2011,
      rating: "9.2",
      seasons: 8,
      episodes: 73,
      poster: "https://image.tmdb.org/t/p/w500/u3bZgnGQ9T01sWNhyveQz0wH0Hl.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/suopoADq0k8YZr4dQXcU6ikQHe6.jpg",
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "Winter Is Coming", titleAr: "الشتاء قادم", duration: "62 min", videoUrl: "https://www.youtube.com/embed/KPLWWIOCOOQ" },
            { ep: 2, title: "The Kingsroad", titleAr: "طريق الملك", duration: "56 min", videoUrl: "https://www.youtube.com/embed/KPLWWIOCOOQ" }
          ]
        }
      ]
    },
    {
      id: "series-3",
      title: "Stranger Things",
      titleAr: "أشياء غريبة",
      description: "A group of kids encounter terrifying supernatural forces and secret government exploits.",
      descriptionAr: "مجموعة من الأطفال تواجه قوى خارقة مرعبة ومؤامرات حكومية سرية.",
      genre: ["Horror", "Sci-Fi", "Drama"],
      year: 2016,
      rating: "8.7",
      seasons: 4,
      episodes: 34,
      poster: "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "The Vanishing of Will Byers", titleAr: "اختفاء ويل باير", duration: "49 min", videoUrl: "https://www.youtube.com/embed/b9EkMc79ZSU" },
            { ep: 2, title: "The Weirdo on Maple Street", titleAr: "الغريب في شارع مابل", duration: "55 min", videoUrl: "https://www.youtube.com/embed/b9EkMc79ZSU" }
          ]
        }
      ]
    },
    {
      id: "series-4",
      title: "The Last of Us",
      titleAr: "ذا لاست أوف أس",
      description: "A hardened survivor and a teenage girl must travel across a post-apocalyptic US.",
      descriptionAr: "رجل صلب وفتاة مراهقة يتنقلان عبر أمريكا في عالم ما بعد الكارثة.",
      genre: ["Drama", "Horror", "Sci-Fi"],
      year: 2023,
      rating: "8.8",
      seasons: 2,
      episodes: 9,
      poster: "https://image.tmdb.org/t/p/w500/uKvVjHNqB5VmOrdxqAt2F7J78ED.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/6ayvIbOEBCNzja3U7SMLqhWiJGF.jpg",
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "When You're Lost in the Darkness", titleAr: "حين تضيع في الظلام", duration: "81 min", videoUrl: "https://www.youtube.com/embed/uLtkt8BonwM" },
            { ep: 2, title: "Infected", titleAr: "المصابون", duration: "55 min", videoUrl: "https://www.youtube.com/embed/uLtkt8BonwM" }
          ]
        }
      ]
    },
    {
      id: "series-5",
      title: "House of the Dragon",
      titleAr: "بيت التنين",
      description: "The story of House Targaryen, set 200 years before the events of Game of Thrones.",
      descriptionAr: "قصة آل تارغاريان قبل 200 سنة من أحداث لعبة العروش.",
      genre: ["Fantasy", "Drama", "History"],
      year: 2022,
      rating: "8.4",
      seasons: 2,
      episodes: 18,
      poster: "https://image.tmdb.org/t/p/w500/t9XkeegN9wrDnCejCEVBuAqNnhS.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/etj8E2o0Bud0HkONVQPjyCkIvpv.jpg",
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "The Heirs of the Dragon", titleAr: "ورثة التنين", duration: "66 min", videoUrl: "https://www.youtube.com/embed/DotnJ7tTA34" },
            { ep: 2, title: "The Rogue Prince", titleAr: "الأمير المارق", duration: "54 min", videoUrl: "https://www.youtube.com/embed/DotnJ7tTA34" }
          ]
        }
      ]
    },
    {
      id: "series-6",
      title: "Squid Game",
      titleAr: "لعبة الحبار",
      description: "Hundreds of cash-strapped players accept a strange invitation to compete in children's games.",
      descriptionAr: "مئات المتسابقين المدينين يقبلون دعوة غريبة للمنافسة في ألعاب أطفال على جائزة ضخمة.",
      genre: ["Drama", "Thriller", "Action"],
      year: 2021,
      rating: "8.0",
      seasons: 2,
      episodes: 16,
      poster: "https://image.tmdb.org/t/p/w500/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg",
      backdrop: "https://image.tmdb.org/t/p/original/qw3J9cNeLioOLoR68WX7z79aCdK.jpg",
      seasons_data: [
        {
          season: 1,
          episodes: [
            { ep: 1, title: "Red Light, Green Light", titleAr: "الضوء الأحمر، الضوء الأخضر", duration: "60 min", videoUrl: "https://www.youtube.com/embed/oqxAJKy0ii4" },
            { ep: 2, title: "Hell", titleAr: "الجحيم", duration: "63 min", videoUrl: "https://www.youtube.com/embed/oqxAJKy0ii4" }
          ]
        }
      ]
    }
  ]
};
