let allListings = [];
let displayed = 0;
const PER_PAGE = 12;

async function loadListings() {
    const resp = await fetch('api/listings.json');
    const data = await resp.json();
    allListings = data.listings;

    document.getElementById('stat-total').textContent = data.total.toLocaleString();
    document.getElementById('stat-sfh').textContent = data.sfh.toLocaleString();
    document.getElementById('stat-mfh').textContent = data.mfh.toLocaleString();
    document.getElementById('stat-land').textContent = data.land.toLocaleString();

    renderFeatured();
    applyFilters();
}

function renderFeatured() {
    const grid = document.getElementById('featured-grid');
    const featured = allListings.filter(l => l.dom <= 3).slice(0, 6);
    grid.innerHTML = featured.map(cardHTML).join('');
}

function applyFilters() {
    const type = document.getElementById('filter-type').value;
    const city = document.getElementById('filter-city').value.toLowerCase().trim();
    const minPrice = parseInt(document.getElementById('filter-min').value) || 0;
    const maxPrice = parseInt(document.getElementById('filter-max').value) || 999999999;
    const beds = parseInt(document.getElementById('filter-beds').value) || 0;
    const sort = document.getElementById('filter-sort').value;

    let filtered = allListings.filter(l => {
        if (type && l.type !== type) return false;
        if (city && !l.city.toLowerCase().includes(city)) return false;
        if (l.price < minPrice || l.price > maxPrice) return false;
        if (beds && l.beds < beds) return false;
        return true;
    });

    if (sort === 'price-asc') filtered.sort((a, b) => a.price - b.price);
    else if (sort === 'price-desc') filtered.sort((a, b) => b.price - a.price);
    else if (sort === 'newest') filtered.sort((a, b) => a.dom - b.dom);
    else if (sort === 'sqft') filtered.sort((a, b) => b.sqft - a.sqft);

    displayed = 0;
    const grid = document.getElementById('listings-grid');
    grid.innerHTML = '';
    document.getElementById('results-count').textContent = `${filtered.length} properties found`;
    window._filtered = filtered;
    showMore();
}

function showMore() {
    const filtered = window._filtered || [];
    const grid = document.getElementById('listings-grid');
    const batch = filtered.slice(displayed, displayed + PER_PAGE);
    grid.innerHTML += batch.map(cardHTML).join('');
    displayed += batch.length;

    const btn = document.getElementById('load-more');
    btn.style.display = displayed >= filtered.length ? 'none' : 'block';
}

function cardHTML(l) {
    const priceStr = '$' + l.price.toLocaleString();
    const domLabel = l.dom === 0 ? 'Just Listed' : l.dom + ' days';
    const meta = [];
    if (l.beds) meta.push(l.beds + ' bd');
    if (l.baths) meta.push(l.baths + ' ba');
    if (l.sqft) meta.push(l.sqft.toLocaleString() + ' sqft');
    if (l.acres && l.type === 'Land') meta.push(l.acres.toFixed(1) + ' acres');

    return `
    <div class="listing-card" onclick="openListing('${l.id}')">
        <div class="listing-img">
            <span class="placeholder-icon">&#127968;</span>
            <span class="price-tag">${priceStr}</span>
            <span class="type-tag">${l.type}</span>
            <span class="dom-tag">${domLabel}</span>
        </div>
        <div class="listing-body">
            <h3>${l.address}</h3>
            <div class="listing-location">${l.city}, MI ${l.zip}</div>
            <div class="listing-meta">${meta.map(m => '<span>' + m + '</span>').join('')}</div>
        </div>
    </div>`;
}

function openListing(id) {
    const l = allListings.find(x => x.id === id);
    if (!l) return;
    const m = document.getElementById('listing-modal');
    document.getElementById('modal-title').textContent = l.address;
    document.getElementById('modal-location').textContent = `${l.city}, MI ${l.zip}`;
    document.getElementById('modal-price').textContent = '$' + l.price.toLocaleString();

    const details = [];
    if (l.beds) details.push(`<strong>${l.beds}</strong> Bedrooms`);
    if (l.baths) details.push(`<strong>${l.baths}</strong> Bathrooms`);
    if (l.sqft) details.push(`<strong>${l.sqft.toLocaleString()}</strong> Sq Ft`);
    if (l.acres) details.push(`<strong>${l.acres.toFixed(2)}</strong> Acres`);
    if (l.dom !== undefined) details.push(`<strong>${l.dom}</strong> Days on Market`);
    if (l.year_built) details.push(`Built <strong>${l.year_built}</strong>`);
    if (l.garage) details.push(`<strong>Garage</strong>`);
    if (l.new_const) details.push(`<strong>New Construction</strong>`);
    if (l.school) details.push(`<strong>${l.school}</strong> School District`);
    document.getElementById('modal-details').innerHTML = details.join('<span class="modal-sep">|</span>');
    document.getElementById('modal-remarks').textContent = l.remarks || 'No remarks available.';
    document.getElementById('modal-agent').textContent = l.agent ? `Listed by ${l.agent} — ${l.agency}` : '';
    m.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('listing-modal').classList.remove('open');
    document.body.style.overflow = '';
}

// Hero search
function heroSearch() {
    const q = document.getElementById('hero-input').value.trim();
    if (!q) return;
    document.getElementById('listings').scrollIntoView({ behavior: 'smooth' });
    const cityInput = document.getElementById('filter-city');
    cityInput.value = q;
    setTimeout(applyFilters, 300);
}

// Nav scroll
window.addEventListener('scroll', () => {
    document.querySelector('nav').classList.toggle('scrolled', window.scrollY > 60);
});

// Mobile menu
function toggleMenu() {
    document.querySelector('.nav-links').classList.toggle('open');
}

// Contact form
function handleContact(e) {
    e.preventDefault();
    const name = e.target.querySelector('[name=name]').value;
    const email = e.target.querySelector('[name=email]').value;
    const phone = e.target.querySelector('[name=phone]').value;
    const msg = e.target.querySelector('[name=message]').value;
    const mailto = `mailto:aiden@michigantopproducers.com?subject=Website Inquiry from ${name}&body=Name: ${name}%0AEmail: ${email}%0APhone: ${phone}%0A%0A${encodeURIComponent(msg)}`;
    window.location.href = mailto;
    e.target.reset();
}

document.addEventListener('DOMContentLoaded', loadListings);
