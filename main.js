/**
 * The Cold Fusion Calendar — Interactive Chronology
 *
 * State lives in:
 *   currentDate, selectedDay, view ('month'|'year'|'person'),
 *   searchTerm, taxFilter (Set), countryFilter (Set), personSlug
 * Reflected to/from location.hash so URLs are shareable.
 */

const DATA_URL = 'datasets/40d7f378-7b62-44f6-8196-5bae64a95169/data.json';
const QUOTES_URL = 'datasets/40d7f378-7b62-44f6-8196-5bae64a95169/quotes.json';
const UPCOMING_COUNT = 8;
const MONTH_NAMES = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const SHORT_MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

class FusionCalendar {
    constructor() {
        this.events = [];
        this.quotes = [];
        this.currentQuoteIndex = -1;
        this.today = new Date();
        this.currentDate = new Date();
        this.selectedDay = this.today.getDate();
        this.view = 'month';
        this.searchTerm = '';
        this.taxFilter = new Set();
        this.countryFilter = new Set();
        this.personSlug = null;
        this.init();
    }

    async init() {
        await this.loadData();
        this.parseHash();
        this.setupEventListeners();
        this.createParticles();
        this.render();
    }

    async loadData() {
        try {
            const [events, quotes] = await Promise.all([
                fetch(DATA_URL).then(r => r.json()),
                fetch(QUOTES_URL).then(r => r.json()).catch(() => [])
            ]);
            this.events = events;
            this.quotes = quotes;
            document.getElementById('eventCount').textContent = this.events.length;
            this.drawQuote();
        } catch (err) {
            console.error('Failed to load historical data:', err);
        }
    }

    /* ------------------------------------------------------------- *
     * URL hash routing (shareable links)
     * #YYYY-M-D, #YYYY, #today, #year-view, #person/<slug>
     * + ?q=, ?tax=, ?country=
     * ------------------------------------------------------------- */
    parseHash() {
        const h = location.hash.slice(1);
        const qIdx = h.indexOf('?');
        const main = qIdx >= 0 ? h.slice(0, qIdx) : h;
        const params = new URLSearchParams(qIdx >= 0 ? h.slice(qIdx + 1) : '');
        if (params.get('q')) this.searchTerm = params.get('q');
        if (params.get('tax')) this.taxFilter = new Set(params.get('tax').split(','));
        if (params.get('country')) this.countryFilter = new Set(params.get('country').split(','));

        if (main === 'today') {
            this.currentDate = new Date(this.today);
            this.selectedDay = this.today.getDate();
            return;
        }
        if (main === 'year-view') { this.view = 'year'; return; }
        const pm = main.match(/^person\/([a-z0-9\-]+)$/);
        if (pm) { this.view = 'person'; this.personSlug = pm[1]; return; }
        const dm = main.match(/^(-?\d{1,5})(?:-(\d{1,2}))?(?:-(\d{1,2}))?$/);
        if (dm) {
            const y = parseInt(dm[1], 10);
            const m = dm[2] ? parseInt(dm[2], 10) - 1 : 0;
            const d = dm[3] ? parseInt(dm[3], 10) : null;
            this.currentDate = new Date(y, m, 1);
            this.currentDate.setFullYear(y);
            if (d) this.selectedDay = d;
        }
    }

    swapOgImage() {
        const m = this.currentDate.getMonth() + 1;
        const d = this.selectedDay || this.today.getDate();
        const url = `https://www.lackluster.org/cf/assets/og/${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}.png`;
        document.querySelectorAll('meta[property="og:image"], meta[name="twitter:image"]').forEach(el => {
            el.setAttribute('content', url);
        });
    }

    syncHash() {
        let main = '';
        if (this.view === 'year') main = 'year-view';
        else if (this.view === 'person' && this.personSlug) main = `person/${this.personSlug}`;
        else {
            const y = this.currentDate.getFullYear();
            const m = this.currentDate.getMonth() + 1;
            main = this.selectedDay ? `${y}-${m}-${this.selectedDay}` : `${y}-${m}`;
        }
        const params = new URLSearchParams();
        if (this.searchTerm) params.set('q', this.searchTerm);
        if (this.taxFilter.size) params.set('tax', [...this.taxFilter].join(','));
        if (this.countryFilter.size) params.set('country', [...this.countryFilter].join(','));
        const qs = params.toString();
        const hash = '#' + main + (qs ? '?' + qs : '');
        history.replaceState({}, '', hash);
    }

    /* ------------------------------------------------------------- *
     * Filter logic
     * ------------------------------------------------------------- */
    matchesFilter(ev) {
        if (this.taxFilter.size && !this.taxFilter.has(ev.taxonomy || 'Research')) return false;
        if (this.countryFilter.size && !this.countryFilter.has(ev.country || 'Global')) return false;
        if (this.searchTerm) {
            const q = this.searchTerm.toLowerCase();
            const hay = `${ev.name} ${ev.blurb} ${ev.year} ${ev.taxonomy} ${ev.country}`.toLowerCase();
            if (!hay.includes(q)) return false;
        }
        return true;
    }

    filteredEvents() { return this.events.filter(e => this.matchesFilter(e)); }

    /* ------------------------------------------------------------- *
     * Quote rotator
     * ------------------------------------------------------------- */
    drawQuote() {
        if (!this.quotes.length) return;
        let i;
        do { i = Math.floor(Math.random() * this.quotes.length); }
        while (this.quotes.length > 1 && i === this.currentQuoteIndex);
        this.currentQuoteIndex = i;
        const el = document.getElementById('quoteText');
        if (el) el.textContent = this.quotes[i];
    }

    async copyText(text, btn) {
        const original = btn.innerHTML;
        try { await navigator.clipboard.writeText(text); }
        catch {
            const ta = document.createElement('textarea');
            ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
            document.body.appendChild(ta); ta.select();
            try { document.execCommand('copy'); } catch {}
            document.body.removeChild(ta);
        }
        btn.classList.add('copied');
        setTimeout(() => { btn.classList.remove('copied'); btn.innerHTML = original; }, 1400);
    }

    /* ------------------------------------------------------------- *
     * Event listeners
     * ------------------------------------------------------------- */
    setupEventListeners() {
        document.getElementById('prevMonth').addEventListener('click', () => this.shiftMonth(-1));
        document.getElementById('nextMonth').addEventListener('click', () => this.shiftMonth(1));
        document.getElementById('todayBtn').addEventListener('click', () => this.jumpToday());
        document.getElementById('copyAllBtn').addEventListener('click', (e) => this.copyAll(e.currentTarget));
        document.getElementById('viewToggleBtn').addEventListener('click', () => this.toggleView());

        document.getElementById('quoteText').addEventListener('click', () => this.drawQuote());
        document.getElementById('quoteShuffleBtn').addEventListener('click', (e) => { e.stopPropagation(); this.drawQuote(); });
        document.getElementById('quoteCopyBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.copyText(this.quotes[this.currentQuoteIndex] || '', e.currentTarget);
        });
        document.getElementById('quoteCopyAllBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            const all = `# Cold Fusion Calendar — Reflections (${this.quotes.length})\n\n` +
                this.quotes.map(q => `- ${q}`).join('\n');
            this.copyText(all, e.currentTarget);
        });

        const yearInput = document.getElementById('yearInput');
        const applyYear = () => {
            const v = parseInt(yearInput.value, 10);
            if (!Number.isNaN(v)) {
                this.currentDate.setFullYear(v);
                this.selectedDay = null;
                this.render();
            }
        };
        yearInput.addEventListener('change', applyYear);
        yearInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') yearInput.blur(); });

        const search = document.getElementById('searchBox');
        search.value = this.searchTerm;
        search.addEventListener('input', (e) => {
            this.searchTerm = e.target.value;
            this.render();
        });

        document.addEventListener('keydown', (e) => {
            const tag = (document.activeElement && document.activeElement.tagName) || '';
            if (tag === 'INPUT' || tag === 'TEXTAREA') return;
            switch (e.key) {
                case 'ArrowLeft':  this.shiftMonth(-1); break;
                case 'ArrowRight': this.shiftMonth(1); break;
                case 'ArrowUp':    this.currentDate.setFullYear(this.currentDate.getFullYear() + 1); this.render(); break;
                case 'ArrowDown':  this.currentDate.setFullYear(this.currentDate.getFullYear() - 1); this.render(); break;
                case 't': case 'T': this.jumpToday(); break;
                case 'y': case 'Y': this.toggleView(); break;
                case '/': e.preventDefault(); search.focus(); search.select(); break;
                case 'Escape':
                    this.searchTerm = ''; search.value = '';
                    this.taxFilter.clear(); this.countryFilter.clear();
                    if (this.view === 'person') this.view = 'month';
                    this.render();
                    break;
            }
        });

        // Bottom-sheet handle for mobile (drag-to-close)
        const handle = document.getElementById('panelHandle');
        if (handle) {
            let startY = 0, startOpen = true;
            handle.addEventListener('touchstart', (e) => {
                startY = e.touches[0].clientY;
                startOpen = document.body.classList.contains('panel-open');
            });
            handle.addEventListener('touchmove', (e) => {
                const dy = e.touches[0].clientY - startY;
                if (startOpen && dy > 60) document.body.classList.remove('panel-open');
                if (!startOpen && dy < -60) document.body.classList.add('panel-open');
            });
            handle.addEventListener('click', () => document.body.classList.toggle('panel-open'));
        }

        window.addEventListener('hashchange', () => {
            this.parseHash();
            this.render();
        });
    }

    shiftMonth(delta) {
        this.currentDate.setMonth(this.currentDate.getMonth() + delta);
        this.selectedDay = null;
        this.render();
    }
    jumpToday() {
        this.view = 'month';
        this.currentDate = new Date(this.today);
        this.selectedDay = this.today.getDate();
        this.render();
    }
    toggleView() {
        this.view = this.view === 'month' ? 'year' : 'month';
        this.render();
    }

    /* ------------------------------------------------------------- *
     * Filter chips
     * ------------------------------------------------------------- */
    renderFilterChips() {
        const container = document.getElementById('filterChips');
        if (!container) return;
        const taxCounts = {}, countryCounts = {};
        for (const e of this.events) {
            const t = e.taxonomy || 'Research';
            const c = e.country || 'Global';
            taxCounts[t] = (taxCounts[t] || 0) + 1;
            countryCounts[c] = (countryCounts[c] || 0) + 1;
        }
        const sortByCount = (counts) => Object.keys(counts).sort((a,b) => counts[b] - counts[a]);
        const taxList = sortByCount(taxCounts).slice(0, 12);
        const countryList = sortByCount(countryCounts).slice(0, 10);

        const chip = (label, count, set, kind) => {
            const active = set.has(label) ? ' active' : '';
            return `<button class="chip${active}" data-kind="${kind}" data-value="${label}">${label}<span class="chip-count">${count}</span></button>`;
        };
        container.innerHTML = `
            <div class="chip-group">
                <span class="chip-label">Type</span>
                ${taxList.map(t => chip(t, taxCounts[t], this.taxFilter, 'tax')).join('')}
            </div>
            <div class="chip-group">
                <span class="chip-label">Origin</span>
                ${countryList.map(c => chip(c, countryCounts[c], this.countryFilter, 'country')).join('')}
            </div>
        `;
        container.querySelectorAll('.chip').forEach(el => {
            el.addEventListener('click', () => {
                const kind = el.dataset.kind, value = el.dataset.value;
                const set = kind === 'tax' ? this.taxFilter : this.countryFilter;
                if (set.has(value)) set.delete(value); else set.add(value);
                this.render();
            });
        });
    }

    /* ------------------------------------------------------------- *
     * Main render dispatch
     * ------------------------------------------------------------- */
    render() {
        document.body.classList.toggle('view-year', this.view === 'year');
        document.body.classList.toggle('view-person', this.view === 'person');

        if (this.view === 'person') {
            this.renderPerson();
        } else {
            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth();
            document.getElementById('monthDisplay').textContent = MONTH_NAMES[month];
            const yearInput = document.getElementById('yearInput');
            if (document.activeElement !== yearInput) yearInput.value = year;

            if (this.view === 'year') {
                this.renderYearGrid(year);
            } else {
                this.renderGrid(year, month);
            }
            this.renderPanel(year, month);
        }
        this.renderFilterChips();
        this.swapOgImage();
        this.syncHash();
    }

    renderGrid(year, month) {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';
        grid.className = 'calendar-grid';
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        for (let i = 0; i < firstDay; i++) {
            const empty = document.createElement('div');
            empty.className = 'day-cell';
            grid.appendChild(empty);
        }
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            cell.className = 'day-cell active';
            const dayEvents = this.events.filter(e => e.month === (month + 1) && e.date === day);
            const matching = dayEvents.filter(e => this.matchesFilter(e));
            if (matching.length > 0) {
                cell.classList.add('has-events');
                const marker = document.createElement('div');
                marker.className = 'event-marker';
                cell.appendChild(marker);
            } else if (dayEvents.length > 0) {
                cell.classList.add('has-events', 'dimmed');
                const marker = document.createElement('div');
                marker.className = 'event-marker';
                cell.appendChild(marker);
            }
            const num = document.createElement('div');
            num.className = 'day-num';
            num.textContent = day;
            cell.appendChild(num);
            cell.addEventListener('click', () => {
                this.selectedDay = day;
                this.render();
                this.scrollToDay(day);
                document.body.classList.add('panel-open');
            });
            const now = this.today;
            if (day === now.getDate() && month === now.getMonth() && year === now.getFullYear()) cell.classList.add('today');
            if (day === this.selectedDay) cell.classList.add('selected');
            grid.appendChild(cell);
        }
    }

    renderYearGrid(year) {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';
        grid.className = 'calendar-grid year-grid';
        for (let m = 0; m < 12; m++) {
            const monthBox = document.createElement('div');
            monthBox.className = 'mini-month';
            const head = document.createElement('div');
            head.className = 'mini-month-head';
            head.textContent = MONTH_NAMES[m];
            head.addEventListener('click', () => {
                this.view = 'month';
                this.currentDate = new Date(year, m, 1);
                this.selectedDay = null;
                this.render();
            });
            monthBox.appendChild(head);
            const days = new Date(year, m + 1, 0).getDate();
            const grid2 = document.createElement('div');
            grid2.className = 'mini-grid';
            for (let d = 1; d <= days; d++) {
                const dayCell = document.createElement('div');
                dayCell.className = 'mini-day';
                const matching = this.events.filter(e => e.month === (m + 1) && e.date === d && this.matchesFilter(e));
                if (matching.length > 0) {
                    dayCell.classList.add('has-events');
                    dayCell.title = `${MONTH_NAMES[m]} ${d}: ${matching.length} event${matching.length === 1 ? '' : 's'}`;
                    dayCell.style.opacity = Math.min(0.4 + matching.length * 0.2, 1);
                }
                if (this.today.getMonth() === m && this.today.getDate() === d && this.today.getFullYear() === year) {
                    dayCell.classList.add('today');
                }
                dayCell.addEventListener('click', () => {
                    this.view = 'month';
                    this.currentDate = new Date(year, m, 1);
                    this.selectedDay = d;
                    this.render();
                    this.scrollToDay(d);
                });
                grid2.appendChild(dayCell);
            }
            monthBox.appendChild(grid2);
            grid.appendChild(monthBox);
        }
    }

    /* ------------------------------------------------------------- *
     * Panel
     * ------------------------------------------------------------- */
    upcomingFrom(fromMonth1, fromDay, n) {
        const startKey = fromMonth1 * 100 + fromDay;
        const annotated = this.filteredEvents().map(e => {
            const key = e.month * 100 + e.date;
            const offset = key >= startKey ? key - startKey : key - startKey + 1300;
            return { ev: e, offset, key };
        });
        annotated.sort((a, b) => a.offset - b.offset || a.ev.year - b.ev.year);
        return annotated.slice(0, n).map(a => a.ev);
    }

    renderPanel(year, month) {
        const panel = document.getElementById('eventDetails');
        const filtered = this.filteredEvents();
        const monthEvents = filtered
            .filter(e => e.month === (month + 1))
            .sort((a, b) => a.date - b.date || a.year - b.year);

        const onTodayMonth = (year === this.today.getFullYear() && month === this.today.getMonth());
        const anchorMonth1 = month + 1;
        const anchorDay = onTodayMonth ? this.today.getDate() : 1;
        const upcoming = this.upcomingFrom(anchorMonth1, anchorDay, UPCOMING_COUNT);

        const todayLabel = `${MONTH_NAMES[month]} ${anchorDay}`;
        const todayMonth1 = this.today.getMonth() + 1;
        const todayDate = this.today.getDate();
        const todayEvents = filtered
            .filter(e => e.month === todayMonth1 && e.date === todayDate)
            .sort((a, b) => a.year - b.year);

        const filterStatus = (this.searchTerm || this.taxFilter.size || this.countryFilter.size)
            ? `<div class="filter-status">Filtered: ${filtered.length}/${this.events.length} events</div>` : '';

        let html = filterStatus + `
            <section class="panel-section today-section">
                <div class="detail-header">
                    <div class="meta">${todayEvents.length ? `${todayEvents.length} milestone${todayEvents.length === 1 ? '' : 's'} on this day` : 'No matching milestones today'}</div>
                    <h3>Today · ${MONTH_NAMES[this.today.getMonth()]} ${todayDate}</h3>
                </div>
                ${todayEvents.length === 0
                    ? `<p class="muted">Nothing recorded for this date${this.searchTerm || this.taxFilter.size || this.countryFilter.size ? ' that matches your filter' : ' — yet'}.</p>`
                    : todayEvents.map(ev => this.eventCardHTML(ev, false, true)).join('')}
            </section>
            <section class="panel-section">
                <div class="detail-header">
                    <div class="meta">${MONTH_NAMES[month]}${monthEvents.length ? ` · ${monthEvents.length} event${monthEvents.length === 1 ? '' : 's'}` : ''}</div>
                    <h3>This Month</h3>
                </div>
                ${monthEvents.length === 0
                    ? `<div class="empty-state"><div class="fusion-ring"></div><p>${(this.searchTerm || this.taxFilter.size || this.countryFilter.size) ? 'No matches in this month.' : 'No recorded milestones this month.'}</p></div>`
                    : monthEvents.map(ev => this.eventCardHTML(ev, true, this.selectedDay === ev.date)).join('')}
            </section>
            <section class="panel-section">
                <div class="detail-header">
                    <div class="meta">From ${todayLabel} onwards</div>
                    <h3>Upcoming Anniversaries</h3>
                </div>
                ${upcoming.map(ev => this.eventCardHTML(ev, true)).join('') || '<p class="muted">No events.</p>'}
            </section>
        `;
        panel.innerHTML = html;
        this.attachPersonClicks(panel);
    }

    /* ------------------------------------------------------------- *
     * Event card HTML
     * ------------------------------------------------------------- */
    formatBlurb(text) {
        const escape = (s) => s.replace(/[&<>"']/g, c => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        })[c]);
        let html = escape(text);
        html = html.replace(/(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        html = html.replace(/Jed Rothwell/g,
            '<a href="https://www.lenr-canr.org" target="_blank" rel="noopener noreferrer">Jed Rothwell</a>');
        return html;
    }

    eventCardHTML(ev, showDate, highlight) {
        const dateLabel = showDate ? `${MONTH_NAMES[ev.month - 1]} ${ev.date}` : '';
        const yearLabel = ev.year > 0 ? ev.year : (ev.year < 0 ? Math.abs(ev.year) + ' BCE' : 'Unspecified Era');
        const slug = personSlug(ev.name);
        return `
            <div class="event-card${highlight ? ' highlight' : ''}" data-day="${ev.date}" data-month="${ev.month}">
                <div class="card-head">
                    ${dateLabel ? `<span class="date-chip">${dateLabel}, ${yearLabel}</span>` : `<span class="date-chip">${yearLabel}</span>`}
                    ${ev.country ? `<span class="origin">${ev.country}</span>` : ''}
                    <span class="taxonomy">${ev.taxonomy || 'Research'}</span>
                </div>
                <div class="name"><a href="#person/${slug}" class="person-link" data-slug="${slug}">${ev.name}</a></div>
                <div class="blurb">${this.formatBlurb(ev.blurb)}</div>
            </div>
        `;
    }

    attachPersonClicks(root) {
        root.querySelectorAll('.person-link').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                this.view = 'person';
                this.personSlug = a.dataset.slug;
                this.render();
            });
        });
    }

    /* ------------------------------------------------------------- *
     * Person view
     * ------------------------------------------------------------- */
    renderPerson() {
        const slug = this.personSlug;
        // Match by exact primary-surname slug (Pons, Stanley == Stanley Pons == "pons")
        // Fallback: substring slug match for compound names like "Pons & Fleischmann"
        const matches = this.events.filter(e => {
            const ps = personSlug(e.name);
            if (ps === slug) return true;
            // Compound names: split on common separators and check each part
            const parts = (e.name || '').split(/[,&/]| and /i).map(p => personSlug(p.trim()));
            return parts.some(p => p === slug);
        });
        const sorted = matches.sort((a, b) => a.year - b.year || a.month - b.month || a.date - b.date);
        const titleCase = (s) => s.split('-').map(w => w[0] ? w[0].toUpperCase() + w.slice(1) : w).join(' ');
        const display = titleCase(slug);
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = `<div class="person-page">
            <button class="back-btn" id="backToCal">← Back to calendar</button>
            <h2 class="person-name">${display}</h2>
            <div class="meta">${sorted.length} entr${sorted.length === 1 ? 'y' : 'ies'} reference this person</div>
        </div>`;
        document.getElementById('backToCal').addEventListener('click', () => {
            this.view = 'month'; this.personSlug = null; this.render();
        });
        const panel = document.getElementById('eventDetails');
        panel.innerHTML = sorted.length
            ? sorted.map(ev => this.eventCardHTML(ev, true, false)).join('')
            : `<p class="muted">No entries found for "${display}". Try clicking a name from the main calendar.</p>`;
        this.attachPersonClicks(panel);
    }

    scrollToDay(day) {
        const panel = document.getElementById('eventDetails');
        const target = panel.querySelector(`.event-card.highlight[data-day="${day}"]`);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    buildClipboardText() {
        const sorted = [...this.events].sort((a, b) =>
            a.year - b.year || a.month - b.month || a.date - b.date);
        const lines = [
            '# The Cold Fusion Calendar', '',
            `${sorted.length} historical milestones in cold fusion and energy science.`,
            'Format: [Month Day, Year] Name (Taxonomy, Country) — Blurb', ''
        ];
        for (const e of sorted) {
            const yearStr = e.year > 0 ? `${e.year}` : (e.year < 0 ? `${Math.abs(e.year)} BCE` : 'Unspecified Era');
            const dateStr = `${MONTH_NAMES[e.month - 1]} ${e.date}, ${yearStr}`;
            const meta = [e.taxonomy, e.country].filter(Boolean).join(', ');
            lines.push(`- [${dateStr}] ${e.name}${meta ? ` (${meta})` : ''} — ${e.blurb}`);
        }
        return lines.join('\n');
    }

    async copyAll(btn) {
        const text = this.buildClipboardText();
        const original = btn.textContent;
        try { await navigator.clipboard.writeText(text); btn.textContent = 'Copied'; }
        catch {
            const ta = document.createElement('textarea');
            ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
            document.body.appendChild(ta); ta.select();
            try { document.execCommand('copy'); btn.textContent = 'Copied'; }
            catch { btn.textContent = 'Copy failed'; }
            document.body.removeChild(ta);
        }
        setTimeout(() => { btn.textContent = original; }, 1800);
    }

    createParticles() {
        const container = document.getElementById('particles');
        const count = 50;
        for (let i = 0; i < count; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            const size = Math.random() * 3 + 1;
            p.style.width = `${size}px`; p.style.height = `${size}px`;
            p.style.left = `${Math.random() * 100}%`; p.style.top = `${Math.random() * 100}%`;
            p.style.opacity = Math.random() * 0.3;
            const duration = Math.random() * 20 + 10;
            p.animate([
                { transform: 'translate(0, 0)' },
                { transform: `translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px)` }
            ], { duration: duration * 1000, iterations: Infinity, direction: 'alternate', easing: 'ease-in-out' });
            container.appendChild(p);
        }
    }
}

/**
 * Normalize an event's `name` field to a primary surname slug.
 * Handles: "Pons, Stanley" → "pons", "Stanley Pons" → "pons",
 *           "Storms, Talcott" → "storms", "F&P" → "f-p" (untouched),
 *           "ICCF-21" → "iccf-21" (untouched), "MITI" → "miti".
 */
function personSlug(s) {
    s = (s || '').trim();
    if (!s) return '';
    // "Surname, Given" → take part before comma
    const comma = s.indexOf(',');
    if (comma > 0) {
        const before = s.slice(0, comma).trim();
        return slugify(before);
    }
    // "Given Middle Surname" with 2+ capitalized words → take last word IF
    // it looks like a person name (not "ICCF-21" or "MIT Wake")
    const words = s.split(/\s+/).filter(Boolean);
    const allCapsOrInitial = words.every(w => /^[A-Z][A-Za-z\.\-]*$/.test(w));
    if (words.length >= 2 && allCapsOrInitial && !/^[A-Z]{3,}$/.test(words[words.length - 1])) {
        // Last word is the surname (e.g., "Stanley Pons" → "pons")
        return slugify(words[words.length - 1]);
    }
    return slugify(s);
}
function slugify(s) {
    return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

window.addEventListener('DOMContentLoaded', () => { new FusionCalendar(); });
