/**
 * The Cold Fusion Calendar - Interactive Chronology
 */

const DATA_URL = 'datasets/40d7f378-7b62-44f6-8196-5bae64a95169/data.json';
const QUOTES_URL = 'datasets/40d7f378-7b62-44f6-8196-5bae64a95169/quotes.json';
const UPCOMING_COUNT = 8;

class FusionCalendar {
    constructor() {
        this.events = [];
        this.quotes = [];
        this.currentQuoteIndex = -1;
        this.currentDate = new Date();
        this.today = new Date();
        this.selectedDay = this.today.getDate();
        this.monthNames = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        this.init();
    }

    async init() {
        await this.loadData();
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
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand('copy'); } catch {}
            document.body.removeChild(ta);
        }
        btn.classList.add('copied');
        setTimeout(() => { btn.classList.remove('copied'); btn.innerHTML = original; }, 1400);
    }

    setupEventListeners() {
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.selectedDay = null;
            this.render();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.selectedDay = null;
            this.render();
        });

        document.getElementById('todayBtn').addEventListener('click', () => {
            this.currentDate = new Date();
            this.selectedDay = this.today.getDate();
            this.render();
        });

        document.getElementById('copyAllBtn').addEventListener('click', (e) => this.copyAll(e.currentTarget));

        document.getElementById('quoteText').addEventListener('click', () => this.drawQuote());
        document.getElementById('quoteShuffleBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.drawQuote();
        });
        document.getElementById('quoteCopyBtn').addEventListener('click', (e) => {
            e.stopPropagation();
            const q = this.quotes[this.currentQuoteIndex] || '';
            this.copyText(q, e.currentTarget);
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
        yearInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { yearInput.blur(); }
        });
    }

    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        document.getElementById('monthDisplay').textContent = this.monthNames[month];
        const yearInput = document.getElementById('yearInput');
        if (document.activeElement !== yearInput) yearInput.value = year;

        this.renderGrid(year, month);
        this.renderPanel(year, month);
    }

    renderGrid(year, month) {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';

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

            if (dayEvents.length > 0) {
                cell.classList.add('has-events');
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
            });

            const now = this.today;
            if (day === now.getDate() && month === now.getMonth() && year === now.getFullYear()) {
                cell.classList.add('today');
            }
            if (day === this.selectedDay) {
                cell.classList.add('selected');
            }

            grid.appendChild(cell);
        }
    }

    /**
     * Returns events sorted by their position in the year-cycle starting at (fromMonth1, fromDay).
     * Each event keyed by month*100+date; wraps around year-end.
     */
    upcomingFrom(fromMonth1, fromDay, n) {
        const startKey = fromMonth1 * 100 + fromDay;
        const annotated = this.events.map(e => {
            const key = e.month * 100 + e.date;
            const offset = key >= startKey ? key - startKey : key - startKey + 1300;
            return { ev: e, offset, key };
        });
        annotated.sort((a, b) => a.offset - b.offset || a.ev.year - b.ev.year);
        return annotated.slice(0, n).map(a => a.ev);
    }

    renderPanel(year, month) {
        const panel = document.getElementById('eventDetails');
        const monthEvents = this.events
            .filter(e => e.month === (month + 1))
            .sort((a, b) => a.date - b.date || a.year - b.year);

        const onTodayMonth = (year === this.today.getFullYear() && month === this.today.getMonth());
        const anchorMonth1 = month + 1;
        const anchorDay = onTodayMonth ? this.today.getDate() : 1;
        const upcoming = this.upcomingFrom(anchorMonth1, anchorDay, UPCOMING_COUNT);

        const todayLabel = `${this.monthNames[month]} ${anchorDay}`;
        const todayMonth1 = this.today.getMonth() + 1;
        const todayDate = this.today.getDate();
        const todayEvents = this.events
            .filter(e => e.month === todayMonth1 && e.date === todayDate)
            .sort((a, b) => a.year - b.year);
        const todayHeader = `Today · ${this.monthNames[this.today.getMonth()]} ${todayDate}`;
        const todaySection = `
            <section class="panel-section today-section">
                <div class="detail-header">
                    <div class="meta">${todayEvents.length ? `${todayEvents.length} milestone${todayEvents.length === 1 ? '' : 's'} on this day` : 'No milestones on this day'}</div>
                    <h3>${todayHeader}</h3>
                </div>
                ${todayEvents.length === 0
                    ? `<p class="muted">Nothing recorded for this date — yet.</p>`
                    : todayEvents.map(ev => this.eventCardHTML(ev, false, true)).join('')
                }
            </section>
        `;
        let html = todaySection + `
            <section class="panel-section">
                <div class="detail-header">
                    <div class="meta">${this.monthNames[month]}${monthEvents.length ? ` · ${monthEvents.length} event${monthEvents.length === 1 ? '' : 's'}` : ''}</div>
                    <h3>This Month</h3>
                </div>
                ${monthEvents.length === 0
                    ? `<div class="empty-state"><div class="fusion-ring"></div><p>No recorded milestones this month.</p></div>`
                    : monthEvents.map(ev => this.eventCardHTML(ev, true, this.selectedDay === ev.date)).join('')
                }
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
    }

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
        const dateLabel = showDate ? `${this.monthNames[ev.month - 1]} ${ev.date}` : '';
        const yearLabel = ev.year > 0 ? ev.year : (ev.year < 0 ? Math.abs(ev.year) + ' BCE' : 'Unspecified Era');
        return `
            <div class="event-card${highlight ? ' highlight' : ''}" data-day="${ev.date}" data-month="${ev.month}">
                <div class="card-head">
                    ${dateLabel ? `<span class="date-chip">${dateLabel}, ${yearLabel}</span>` : `<span class="date-chip">${yearLabel}</span>`}
                    ${ev.country ? `<span class="origin">${ev.country}</span>` : ''}
                    <span class="taxonomy">${ev.taxonomy || 'Research'}</span>
                </div>
                <div class="name">${ev.name}</div>
                <div class="blurb">${this.formatBlurb(ev.blurb)}</div>
            </div>
        `;
    }

    scrollToDay(day) {
        const panel = document.getElementById('eventDetails');
        const target = panel.querySelector(`.event-card.highlight[data-day="${day}"]`);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    buildClipboardText() {
        const sorted = [...this.events].sort((a, b) =>
            a.year - b.year || a.month - b.month || a.date - b.date
        );
        const lines = [
            '# The Cold Fusion Calendar',
            '',
            `${sorted.length} historical milestones in cold fusion and energy science.`,
            'Format: [Month Day, Year] Name (Taxonomy, Country) — Blurb',
            ''
        ];
        for (const e of sorted) {
            const yearStr = e.year > 0 ? `${e.year}` : (e.year < 0 ? `${Math.abs(e.year)} BCE` : 'Unspecified Era');
            const dateStr = `${this.monthNames[e.month - 1]} ${e.date}, ${yearStr}`;
            const meta = [e.taxonomy, e.country].filter(Boolean).join(', ');
            lines.push(`- [${dateStr}] ${e.name}${meta ? ` (${meta})` : ''} — ${e.blurb}`);
        }
        return lines.join('\n');
    }

    async copyAll(btn) {
        const text = this.buildClipboardText();
        const original = btn.textContent;
        try {
            await navigator.clipboard.writeText(text);
            btn.textContent = 'Copied';
        } catch (err) {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
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
            p.style.width = `${size}px`;
            p.style.height = `${size}px`;
            p.style.left = `${Math.random() * 100}%`;
            p.style.top = `${Math.random() * 100}%`;
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

window.addEventListener('DOMContentLoaded', () => { new FusionCalendar(); });
