/**
 * ============================================================
 *  STREAMIFY — Main App Logic
 * ============================================================
 */

// ─── Globals ─────────────────────────────────────────────────
const ALL_CONTENT = [
  ...STREAMIFY_DATA.movies.map(m => ({ ...m, type: 'movie' })),
  ...STREAMIFY_DATA.series.map(s => ({ ...s, type: 'series' }))
];

// ─── DOM Ready ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

  // ── 1. Hide Loader ─────────────────────────────────────────
  setTimeout(() => {
    const loader = document.getElementById('loader');
    if (loader) loader.classList.add('hidden');
  }, 1200);

  // ── 2. Detect which page we're on ──────────────────────────
  const page = document.body.dataset.page || 'home';

  // ── 3. Init Navbar ─────────────────────────────────────────
  initNavbar();
  initSearch();

  // ── 4. Page-specific init ──────────────────────────────────
  if (page === 'home')   initHomePage();
  if (page === 'browse') initBrowsePage();
  if (page === 'player') initPlayerPage();
});

// ═══════════════════════════════════════════════════════════
//  NAVBAR
// ═══════════════════════════════════════════════════════════
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  // Scroll effect: add solid background when scrolled
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
      navbar.classList.remove('transparent');
    } else {
      navbar.classList.remove('scrolled');
      navbar.classList.add('transparent');
    }
  });

  // Trigger immediately
  window.dispatchEvent(new Event('scroll'));

  // Highlight active nav link
  const currentFile = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === currentFile || (currentFile === '' && href === 'index.html'))) {
      link.classList.add('active');
    }
  });
}

// ═══════════════════════════════════════════════════════════
//  SEARCH OVERLAY
// ═══════════════════════════════════════════════════════════
function initSearch() {
  const overlay    = document.getElementById('searchOverlay');
  const searchBtn  = document.querySelector('.search-btn');
  const closeBtn   = document.querySelector('.search-overlay-close');
  const input      = document.getElementById('searchInput');
  const results    = document.getElementById('searchResults');

  if (!overlay || !searchBtn) return;

  // Open/close
  searchBtn.addEventListener('click', () => {
    overlay.classList.add('active');
    setTimeout(() => input && input.focus(), 100);
  });

  [closeBtn].forEach(el => {
    if (el) el.addEventListener('click', () => overlay.classList.remove('active'));
  });

  // Close on backdrop click
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.remove('active');
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') overlay.classList.remove('active');
  });

  // Live search
  if (input) {
    let debounceTimer;
    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = input.value.trim().toLowerCase();
        if (!results) return;

        if (!query) {
          results.innerHTML = '';
          return;
        }

        const found = ALL_CONTENT.filter(item =>
          item.title.toLowerCase().includes(query) ||
          (item.titleAr && item.titleAr.includes(query)) ||
          (item.genre && item.genre.some(g => g.toLowerCase().includes(query)))
        ).slice(0, 12);

        results.innerHTML = found.length
          ? found.map(item => createCardHTML(item)).join('')
          : `<div class="no-results"><span class="icon">🎬</span>لا توجد نتائج لـ "${input.value}"</div>`;

        // Attach click handlers to new cards
        results.querySelectorAll('.content-card').forEach(card => {
          card.addEventListener('click', () => goToPlayer(card.dataset.id, card.dataset.type));
        });
      }, 300);
    });
  }
}

// ═══════════════════════════════════════════════════════════
//  HOME PAGE
// ═══════════════════════════════════════════════════════════
function initHomePage() {

  // ── Hero Section ───────────────────────────────────────────
  renderHero();

  // ── Content Rows ───────────────────────────────────────────
  renderSection('trendingRow',  ALL_CONTENT.slice(0, 6),   false);
  renderSection('moviesRow',    STREAMIFY_DATA.movies.map(m => ({ ...m, type: 'movie' })));
  renderSection('seriesRow',    STREAMIFY_DATA.series.map(s => ({ ...s, type: 'series' })), true);

  // ── Scroll animations ──────────────────────────────────────
  observeSections();
}

function renderHero() {
  const heroEl = document.querySelector('.hero');
  if (!heroEl) return;

  const feat = STREAMIFY_DATA.featured;
  if (!feat) return;

  // Set backdrop image
  const bg = heroEl.querySelector('.hero-bg');
  if (bg) bg.style.backgroundImage = `url('${feat.backdrop || feat.poster}')`;

  // Fill hero content
  const titleEl = heroEl.querySelector('.hero-title');
  if (titleEl) titleEl.textContent = feat.titleAr || feat.title;

  const descEl = heroEl.querySelector('.hero-desc');
  if (descEl) descEl.textContent = feat.descriptionAr || feat.description;

  const ratingEl = heroEl.querySelector('.hero-rating');
  if (ratingEl) ratingEl.textContent = feat.rating;

  const yearEl = heroEl.querySelector('.hero-year');
  if (yearEl) yearEl.textContent = feat.year;

  const durEl = heroEl.querySelector('.hero-duration');
  if (durEl) durEl.textContent = feat.duration || (feat.seasons ? `${feat.seasons} مواسم` : '');

  // Genres
  const genreWrap = heroEl.querySelector('.hero-genres');
  if (genreWrap && feat.genre) {
    genreWrap.innerHTML = feat.genre.slice(0, 3)
      .map(g => `<span class="genre-tag">${g}</span>`).join('');
  }

  // Play button
  const playBtn = heroEl.querySelector('.hero-play-btn');
  if (playBtn) {
    playBtn.addEventListener('click', () => goToPlayer(feat.id, feat.type || 'movie'));
  }

  // Info button
  const infoBtn = heroEl.querySelector('.hero-info-btn');
  if (infoBtn) {
    infoBtn.addEventListener('click', () => goToPlayer(feat.id, feat.type || 'movie'));
  }
}

function renderSection(rowId, items, isSeries = false) {
  const container = document.getElementById(rowId);
  if (!container) return;

  if (isSeries) container.classList.add('series-row');

  container.innerHTML = items.map(item => createCardHTML(item)).join('');

  // Attach click handlers
  container.querySelectorAll('.content-card').forEach(card => {
    card.addEventListener('click', () => goToPlayer(card.dataset.id, card.dataset.type));
  });
}

// ═══════════════════════════════════════════════════════════
//  BROWSE PAGE
// ═══════════════════════════════════════════════════════════
function initBrowsePage() {
  const grid = document.getElementById('browseGrid');
  if (!grid) return;

  let currentFilter = 'all';
  let currentGenre  = 'all';

  function renderBrowse() {
    let items = ALL_CONTENT;

    if (currentFilter === 'movies')  items = items.filter(i => i.type === 'movie');
    if (currentFilter === 'series')  items = items.filter(i => i.type === 'series');

    if (currentGenre !== 'all') {
      items = items.filter(i => i.genre && i.genre.includes(currentGenre));
    }

    grid.innerHTML = items.length
      ? items.map(item => createCardHTML(item)).join('')
      : `<div class="no-results"><span class="icon">🎬</span>لا يوجد محتوى في هذه الفئة</div>`;

    grid.querySelectorAll('.content-card').forEach(card => {
      card.addEventListener('click', () => goToPlayer(card.dataset.id, card.dataset.type));
    });

    // Animate cards in
    grid.querySelectorAll('.content-card').forEach((card, i) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      setTimeout(() => {
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, i * 40);
    });
  }

  // Type filter buttons
  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderBrowse();
    });
  });

  // Genre filter buttons
  document.querySelectorAll('.filter-btn[data-genre]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn[data-genre]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentGenre = btn.dataset.genre;
      renderBrowse();
    });
  });

  renderBrowse();
}

// ═══════════════════════════════════════════════════════════
//  PLAYER PAGE
// ═══════════════════════════════════════════════════════════
function initPlayerPage() {
  // Read content ID & type from URL params
  const params  = new URLSearchParams(location.search);
  const id      = params.get('id');
  const type    = params.get('type') || 'movie';

  if (!id) {
    window.location.href = 'index.html';
    return;
  }

  // Find content
  let content;
  if (type === 'movie') {
    content = STREAMIFY_DATA.movies.find(m => m.id === id)
           || (STREAMIFY_DATA.featured.id === id ? STREAMIFY_DATA.featured : null);
  } else {
    content = STREAMIFY_DATA.series.find(s => s.id === id);
  }

  if (!content) { window.location.href = 'index.html'; return; }

  // Set page title
  document.title = `${content.titleAr || content.title} — Streamify`;

  // Set backdrop
  const backdropEl = document.querySelector('.player-backdrop');
  if (backdropEl) backdropEl.style.backgroundImage = `url('${content.backdrop || content.poster}')`;

  // Set video
  const videoWrap = document.getElementById('videoWrap');
  if (videoWrap) {
    const videoUrl = content.videoUrl || '';
    if (videoUrl.includes('youtube.com') || videoUrl.includes('drive.google.com')) {
      videoWrap.innerHTML = `<iframe src="${videoUrl}" allowfullscreen allow="autoplay; encrypted-media" title="${content.title}"></iframe>`;
    } else if (videoUrl) {
      videoWrap.innerHTML = `<video controls src="${videoUrl}" poster="${content.poster}"></video>`;
    } else {
      videoWrap.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100%;color:#9090b0;font-family:'Rajdhani',sans-serif;font-size:1.1rem;letter-spacing:0.05em;flex-direction:column;gap:1rem;">
          <span style="font-size:3rem">🎬</span>
          الفيديو غير متاح حالياً — أضف الرابط في content.js
        </div>`;
    }
  }

  // Fill content info
  const titleEl = document.getElementById('contentTitle');
  if (titleEl) titleEl.textContent = content.titleAr || content.title;

  const descEl = document.getElementById('contentDesc');
  if (descEl) descEl.textContent = content.descriptionAr || content.description;

  const yearEl = document.getElementById('contentYear');
  if (yearEl) yearEl.textContent = content.year;

  const ratingEl = document.getElementById('contentRating');
  if (ratingEl) ratingEl.textContent = `⭐ ${content.rating}`;

  const durEl = document.getElementById('contentDuration');
  if (durEl) durEl.textContent = content.duration || (content.seasons ? `${content.seasons} مواسم` : '');

  const genreEl = document.getElementById('contentGenres');
  if (genreEl && content.genre) {
    genreEl.innerHTML = content.genre.map(g => `<span class="genre-tag">${g}</span>`).join('');
  }

  // ── Episodes (series only) ──────────────────────────────────
  if (type === 'series' && content.seasons_data) {
    renderEpisodes(content, videoWrap);
  } else {
    const episodesPanel = document.getElementById('episodesPanel');
    if (episodesPanel) episodesPanel.style.display = 'none';
  }

  // ── Related content ─────────────────────────────────────────
  renderRelated(content, type);

  // ── Back button ─────────────────────────────────────────────
  const backBtn = document.querySelector('.back-btn');
  if (backBtn) backBtn.addEventListener('click', () => history.back());
}

function renderEpisodes(content, videoWrap) {
  const panel        = document.getElementById('episodesPanel');
  const seasonSel    = document.getElementById('seasonSelector');
  const epList       = document.getElementById('episodesList');

  if (!panel || !seasonSel || !epList) return;

  let currentSeason = 0;
  let currentEpIdx  = 0;

  function loadSeason(seasonIdx) {
    currentSeason = seasonIdx;
    const seasonData = content.seasons_data[seasonIdx];
    if (!seasonData) return;

    // Render season buttons
    seasonSel.innerHTML = content.seasons_data.map((s, i) =>
      `<button class="season-btn ${i === seasonIdx ? 'active' : ''}" data-season="${i}">
        الموسم ${s.season}
      </button>`
    ).join('');

    seasonSel.querySelectorAll('.season-btn').forEach(btn => {
      btn.addEventListener('click', () => loadSeason(+btn.dataset.season));
    });

    // Render episodes
    epList.innerHTML = seasonData.episodes.map((ep, i) =>
      `<div class="episode-item ${i === currentEpIdx && seasonIdx === currentSeason ? 'active' : ''}" data-ep="${i}" data-season="${seasonIdx}">
        <div class="ep-num">${ep.ep}</div>
        <div class="ep-info">
          <div class="ep-title">${ep.titleAr || ep.title}</div>
          <div class="ep-duration">${ep.duration}</div>
        </div>
      </div>`
    ).join('');

    // Episode click
    epList.querySelectorAll('.episode-item').forEach(el => {
      el.addEventListener('click', () => {
        epList.querySelectorAll('.episode-item').forEach(e => e.classList.remove('active'));
        el.classList.add('active');
        currentEpIdx = +el.dataset.ep;
        const ep = content.seasons_data[currentSeason].episodes[currentEpIdx];
        if (ep && videoWrap) {
          const url = ep.videoUrl || '';
          if (url.includes('youtube.com') || url.includes('drive.google.com')) {
            videoWrap.innerHTML = `<iframe src="${url}" allowfullscreen allow="autoplay; encrypted-media" title="${ep.title}"></iframe>`;
          } else if (url) {
            videoWrap.innerHTML = `<video controls src="${url}"></video>`;
          }
          // Scroll to video
          videoWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  loadSeason(0);
}

function renderRelated(content, type) {
  const relatedGrid = document.getElementById('relatedGrid');
  if (!relatedGrid) return;

  const related = ALL_CONTENT
    .filter(item => item.id !== content.id && item.type === type)
    .slice(0, 6);

  relatedGrid.innerHTML = related.map(item => createCardHTML(item)).join('');

  relatedGrid.querySelectorAll('.content-card').forEach(card => {
    card.addEventListener('click', () => goToPlayer(card.dataset.id, card.dataset.type));
  });
}

// ═══════════════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════════════

/**
 * Creates the HTML for a content card
 */
function createCardHTML(item) {
  const typeLabel = item.type === 'movie' ? 'فيلم' : 'مسلسل';
  const subLabel  = item.type === 'movie'
    ? `<span>📅 ${item.year}</span><span>⏱ ${item.duration || '—'}</span>`
    : `<span>📺 ${item.seasons || '?'} مواسم</span><span>📅 ${item.year}</span>`;

  return `
    <div class="content-card" data-id="${item.id}" data-type="${item.type}">
      <div class="card-poster">
        <img src="${item.poster}" alt="${item.titleAr || item.title}" loading="lazy"
             onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'300\' height=\'450\' viewBox=\'0 0 300 450\'%3E%3Crect fill=\'%2312121f\' width=\'300\' height=\'450\'/%3E%3Ctext fill=\'%235a5a7a\' font-size=\'48\' text-anchor=\'middle\' x=\'150\' y=\'240\'%3E🎬%3C/text%3E%3C/svg%3E'">
        <div class="card-rating-badge">⭐ ${item.rating}</div>
        <div class="card-type-badge ${item.type}">${typeLabel}</div>
        <div class="card-overlay">
          <div class="card-play-btn">▶</div>
        </div>
      </div>
      <div class="card-info">
        <div class="card-title">${item.titleAr || item.title}</div>
        <div class="card-subtitle">${subLabel}</div>
      </div>
    </div>`;
}

/**
 * Navigate to the player page
 */
function goToPlayer(id, type) {
  window.location.href = `player.html?id=${id}&type=${type}`;
}

/**
 * Intersection Observer for scroll animations
 */
function observeSections() {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.section').forEach(el => observer.observe(el));
}

/**
 * Show a toast notification
 */
function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}
