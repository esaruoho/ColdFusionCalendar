/**
 * The Fusion Calendar - Interactive Chronology
 */

const DATA_URL = '/datasets/40d7f378-7b62-44f6-8196-5bae64a95169/data.json';

class FusionCalendar {
    constructor() {
        this.events = [];
        this.currentDate = new Date();
        this.selectedDate = null;
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
            const response = await fetch(DATA_URL);
            this.events = await response.json();
            document.getElementById('eventCount').textContent = this.events.length;
        } catch (err) {
            console.error('Failed to load historical data:', err);
        }
    }

    setupEventListeners() {
        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.render();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.render();
        });
    }

    render() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();

        document.getElementById('monthDisplay').textContent = this.monthNames[month];
        document.getElementById('yearDisplay').textContent = year;

        this.renderGrid(year, month);
    }

    renderGrid(year, month) {
        const grid = document.getElementById('calendarGrid');
        grid.innerHTML = '';

        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Previous month empty cells
        for (let i = 0; i < firstDay; i++) {
            const empty = document.createElement('div');
            empty.className = 'day-cell';
            grid.appendChild(empty);
        }

        // Current month cells
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            cell.className = 'day-cell active';
            
            // Check for events on this day (ignoring year for anniversary view)
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

            cell.addEventListener('click', () => this.selectDay(day, dayEvents, cell));

            // Today highlight
            const now = new Date();
            if (day === now.getDate() && month === now.getMonth() && year === now.getFullYear()) {
                cell.classList.add('today');
            }

            grid.appendChild(cell);
        }
    }

    selectDay(day, dayEvents, cellElement) {
        // Clear previous selection
        const selected = document.querySelector('.day-cell.selected');
        if (selected) selected.classList.remove('selected');

        cellElement.classList.add('selected');
        this.renderDetails(day, dayEvents);
    }

    renderDetails(day, events) {
        const detailsPanel = document.getElementById('eventDetails');
        
        if (!events || events.length === 0) {
            detailsPanel.innerHTML = `
                <div class="empty-state">
                    <div class="fusion-ring"></div>
                    <p>On this day, the fusion of ideas continues in silence.</p>
                </div>
            `;
            return;
        }

        const monthName = this.monthNames[this.currentDate.getMonth()];
        
        let html = `
            <div class="detail-header">
                <div class="meta">${monthName} ${day}</div>
                <h3>Chronicle</h3>
            </div>
        `;

        events.forEach(event => {
            html += `
                <div class="event-card">
                    <span class="taxonomy">${event.taxonomy || 'Research'}</span>
                    <div class="name">${event.name}</div>
                    <div class="blurb">"${event.blurb}"</div>
                    <span class="year">${event.year > 0 ? event.year : (event.year < 0 ? Math.abs(event.year) + ' BCE' : 'Unspecified Era')}</span>
                    ${event.country ? `<div class="meta" style="margin-top:0.5rem; font-size: 0.6rem; opacity: 0.6;">Origin: ${event.country}</div>` : ''}
                </div>
            `;
        });

        detailsPanel.innerHTML = html;
        detailsPanel.scrollTop = 0;
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
            
            // Animation
            const duration = Math.random() * 20 + 10;
            p.animate([
                { transform: 'translate(0, 0)' },
                { transform: `translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px)` }
            ], {
                duration: duration * 1000,
                iterations: Infinity,
                direction: 'alternate',
                easing: 'ease-in-out'
            });

            container.appendChild(p);
        }
    }
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    new FusionCalendar();
});
