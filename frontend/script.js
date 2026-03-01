document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');

    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const resultsGrid = document.getElementById('resultsGrid');

    let currentResults = [];

    // Backend endpoint
    const API_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000'
        : 'https://budgetmart-backend.onrender.com'; // Replace with actual deployed backend URL

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        const locationInputHTML = document.getElementById('locationInput');
        const locationQuery = locationInputHTML ? locationInputHTML.value.trim() : "";

        if (!query) return;

        await fetchResults(query, locationQuery);
    });

    sortSelect.addEventListener('change', () => {
        if (currentResults.length > 0) {
            renderResults();
        }
    });

    async function fetchResults(query, locationQuery) {
        // Reset UI
        resultsGrid.innerHTML = '';
        errorMessage.classList.add('hidden');
        loader.classList.remove('hidden');
        currentResults = [];

        try {
            let fetchUrl = `${API_URL}/search?product=${encodeURIComponent(query)}`;
            if (locationQuery) {
                fetchUrl += `&location=${encodeURIComponent(locationQuery)}`;
            }

            const response = await fetch(fetchUrl);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to fetch results');
            }

            const data = await response.json();
            currentResults = data;

            // Artificial tiny delay for smooth animation transition
            setTimeout(() => {
                loader.classList.add('hidden');
                renderResults();
            }, 500);

        } catch (error) {
            loader.classList.add('hidden');
            errorText.textContent = error.message;
            errorMessage.classList.remove('hidden');
        }
    }

    function sortResults(results) {
        const sortBy = sortSelect.value;
        let sorted = [...results];

        // Ensure "Out of Stock" items are generally pushed back unless specific sorting says otherwise
        if (sortBy === 'price_asc') {
            sorted.sort((a, b) => {
                // If one is OOS and other isn't, the in-stock one wins
                if (!a.stock && b.stock) return 1;
                if (a.stock && !b.stock) return -1;
                // Otherwise normal price sort
                return (a.price || Infinity) - (b.price || Infinity);
            });
        } else if (sortBy === 'availability') {
            sorted.sort((a, b) => {
                if (!a.stock && b.stock) return 1;
                if (a.stock && !b.stock) return -1;
                return 0; // maintain original order for in-stock
            });
        }
        return sorted;
    }

    function renderResults() {
        resultsGrid.innerHTML = '';

        if (currentResults.length === 0) {
            errorText.textContent = "No products found.";
            errorMessage.classList.remove('hidden');
            return;
        }

        const sortedResults = sortResults(currentResults);

        // Find the absolute cheapest in-stock item to highlight
        const inStockItems = sortedResults.filter(r => r.stock && r.price !== null);
        let lowestPrice = Infinity;
        if (inStockItems.length > 0) {
            lowestPrice = Math.min(...inStockItems.map(item => item.price));
        }

        sortedResults.forEach((item, index) => {
            const isBestValue = item.stock && item.price === lowestPrice && item.price !== null;
            const isOoS = !item.stock || item.price === null;

            // Generate a random stable color based on platform name string
            let hash = 0;
            for (let i = 0; i < item.platform.length; i++) {
                hash = item.platform.charCodeAt(i) + ((hash << 5) - hash);
            }
            const color = `hsl(${Math.abs(hash) % 360}, 70%, 50%)`;

            const stockStatusClass = isOoS ? 'status-oos' : 'status-in-stock';
            const stockStatusText = isOoS ? 'Out of Stock' : 'In Stock';

            // Create card
            const card = document.createElement('div');
            card.className = `card ${isBestValue ? 'best-value' : ''} ${isOoS ? 'out-of-stock' : ''}`;
            card.style.animationDelay = `${index * 0.1}s`; // Staggered entrance animation

            const imgHTML = item.image_url ? `<img src="${item.image_url}" alt="${item.product_name}" class="product-img">` : '';

            card.innerHTML = `
                ${imgHTML}
                <div class="card-header">
                    <span class="platform-badge" style="color: ${color}">${item.platform}</span>
                </div>
                
                <h3 class="product-name">${item.product_name}</h3>
                
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <span class="status-badge ${stockStatusClass}">${stockStatusText}</span>
                    ${item.quantity ? `<span class="status-badge" style="background: rgba(124, 58, 237, 0.1); color: var(--accent-primary);"><i class="fa-solid fa-weight-hanging" style="margin-right: 5px;"></i>${item.quantity}</span>` : ''}
                </div>
                
                <div class="price-container">
                    ${!isOoS ? `<span class="currency">₹</span><span class="price">${item.price}</span>` : '<span class="price">--</span>'}
                </div>
                
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 5px; min-height: 18px;">
                    ${!isOoS && item.delivery ? `<i class="fa-solid fa-truck" style="margin-right: 5px;"></i> ${item.delivery}` : ''}
                </div>
                
                <a href="${item.product_url}" target="_blank" class="visit-btn">
                    Visit Store <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 0.8rem; margin-left: 5px;"></i>
                </a>
            `;

            resultsGrid.appendChild(card);
        });
    }
});