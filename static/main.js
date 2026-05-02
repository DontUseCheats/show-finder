document.addEventListener('DOMContentLoaded', () => {
    const navItems    = document.querySelectorAll('.artist-nav-item');
    const heroAvatar  = document.querySelector('.artist-hero-avatar');
    const heroName    = document.querySelector('.artist-hero-name');
    const heroMeta    = document.querySelector('.artist-hero-meta');
    const concertList = document.getElementById('concert-list');
    const sortPills   = document.querySelectorAll('.sort-pill');

    let currentSort = 'date';
    let userCoords  = null;

    // ── Haversine distance in miles ──────────────────────────────────────
    function haversine(lat1, lng1, lat2, lng2) {
        const R = 3958.8;
        const rad = d => d * Math.PI / 180;
        const dLat = rad(lat2 - lat1);
        const dLng = rad(lng2 - lng1);
        const a = Math.sin(dLat / 2) ** 2
                + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2;
        return R * 2 * Math.asin(Math.sqrt(a));
    }

    // ── Sort helpers ─────────────────────────────────────────────────────
    function applyDateSort() {
        const cards = Array.from(concertList.querySelectorAll('.concert-card-full'));
        cards.sort((a, b) =>
            (a.dataset.date || '9999').localeCompare(b.dataset.date || '9999')
        );
        cards.forEach(c => concertList.appendChild(c));
    }

    function applyDistanceSort(coords) {
        const cards = Array.from(concertList.querySelectorAll('.concert-card-full'));

        cards.sort((a, b) => {
            const latA = parseFloat(a.dataset.lat), lngA = parseFloat(a.dataset.lng);
            const latB = parseFloat(b.dataset.lat), lngB = parseFloat(b.dataset.lng);
            if (isNaN(latA)) return  1;
            if (isNaN(latB)) return -1;
            return haversine(coords.latitude, coords.longitude, latA, lngA)
                 - haversine(coords.latitude, coords.longitude, latB, lngB);
        });

        cards.forEach(c => {
            const lat = parseFloat(c.dataset.lat);
            const lng = parseFloat(c.dataset.lng);
            const locEl = c.querySelector('.concert-location-text');
            if (locEl && !isNaN(lat) && !isNaN(lng)) {
                const dist = haversine(coords.latitude, coords.longitude, lat, lng);
                // strip any previous distance label before re-adding
                locEl.textContent = locEl.textContent.replace(/\s*—\s*[\d.]+ mi away/, '').trim()
                    + ` — ${dist.toFixed(1)} mi away`;
            }
            concertList.appendChild(c);
        });
    }

    function applySort() {
        if (currentSort === 'date') {
            applyDateSort();
            return;
        }
        // Distance sort: request geolocation once and cache it
        if (userCoords) {
            applyDistanceSort(userCoords);
        } else {
            navigator.geolocation.getCurrentPosition(
                pos => { userCoords = pos.coords; applyDistanceSort(userCoords); },
                ()  => { applyDateSort(); }   // fallback if permission denied
            );
        }
    }

    // ── Load concerts for a given artist ─────────────────────────────────
    function loadConcerts(artistName, imgSrc) {
        if (heroName) heroName.textContent = artistName;
        if (heroAvatar && heroAvatar.tagName === 'IMG' && imgSrc) {
            heroAvatar.src = imgSrc;
            heroAvatar.alt = artistName;
        }
        if (heroMeta) heroMeta.innerHTML = '<span class="accent">Loading…</span>';
        concertList.innerHTML = '<p class="no-shows">Loading shows…</p>';

        fetch('/artist/' + encodeURIComponent(artistName))
            .then(res => res.text())
            .then(html => {
                concertList.innerHTML = html.trim();
                const count = concertList.querySelectorAll('.concert-card-full').length;
                if (heroMeta) {
                    heroMeta.innerHTML = count
                        ? `<span class="accent">${count} show${count !== 1 ? 's' : ''}</span> found`
                        : '<span class="accent">No upcoming shows</span> found';
                }
                if (count) applySort();
            })
            .catch(() => {
                if (heroMeta) heroMeta.innerHTML = '<span class="accent">Error</span> loading shows';
                concertList.innerHTML = '<p class="no-shows">Could not load shows. Try again.</p>';
            });
    }

    // ── Sort pill clicks ──────────────────────────────────────────────────
    sortPills.forEach(pill => {
        pill.addEventListener('click', () => {
            sortPills.forEach(p => p.classList.remove('sort-pill--active'));
            pill.classList.add('sort-pill--active');
            currentSort = pill.dataset.sort;
            applySort();
        });
    });

    // ── Artist sidebar clicks ─────────────────────────────────────────────
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            loadConcerts(item.dataset.artist, item.dataset.img);
        });
    });

    // Auto-load the first (active) artist on page open
    const first = document.querySelector('.artist-nav-item.active');
    if (first) loadConcerts(first.dataset.artist, first.dataset.img);
});
