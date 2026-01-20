// Mock Data
const products = [
    {
        id: 1,
        title: "Nike Air Max 270",
        brand: "nike",
        price: 899,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Nike+Air+Max",
        isNew: true
    },
    {
        id: 2,
        title: "Adidas Ultraboost 22",
        brand: "adidas",
        price: 1099,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Adidas+Ultraboost",
        isNew: false
    },
    {
        id: 3,
        title: "Puma RS-X",
        brand: "puma",
        price: 799,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Puma+RS-X",
        isNew: false
    },
    {
        id: 4,
        title: "Nike Air Force 1",
        brand: "nike",
        price: 749,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Nike+AF1",
        isNew: false
    },
    {
        id: 5,
        title: "Reebok Classic Leather",
        brand: "reebok",
        price: 599,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Reebok+Classic",
        isNew: false
    },
    {
        id: 6,
        title: "Adidas Forum Low",
        brand: "adidas",
        price: 699,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Adidas+Forum",
        isNew: true
    },
    {
        id: 7,
        title: "Nike Zoom Pegasus",
        brand: "nike",
        price: 949,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Nike+Pegasus",
        isNew: true
    },
    {
        id: 8,
        title: "Puma Suede Classic",
        brand: "puma",
        price: 549,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Puma+Suede",
        isNew: false
    },
    {
        id: 9,
        title: "Reebok Club C 85",
        brand: "reebok",
        price: 649,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Reebok+Club+C",
        isNew: false
    },
    {
        id: 10,
        title: "Nike Dunk Low",
        brand: "nike",
        price: 849,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Nike+Dunk",
        isNew: true
    },
    {
        id: 11,
        title: "Adidas Stan Smith",
        brand: "adidas",
        price: 699,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Adidas+Stan+Smith",
        isNew: false
    },
    {
        id: 12,
        title: "Puma Cali",
        brand: "puma",
        price: 699,
        image: "https://placehold.co/600x600/f5f5f5/333?text=Puma+Cali",
        isNew: false
    }
];

// State
let state = {
    products: products,
    filters: {
        brands: [],
        maxPrice: 1000
    },
    sortBy: 'featured'
};

// DOM Elements
const productsGrid = document.getElementById('products-grid');
const visibleCount = document.getElementById('visible-count');
const brandFilters = document.querySelectorAll('input[name="brand"]');
const priceSlider = document.getElementById('price-slider');
const priceValue = document.getElementById('price-value');
const sortSelect = document.getElementById('sort-select');
const clearFiltersBtn = document.getElementById('clear-filters');
const filterToggleBtn = document.querySelector('.filter-toggle-btn');
const filtersSidebar = document.querySelector('.filters-sidebar');
const mobileApplyBtn = document.querySelector('.mobile-apply-btn');

// Initialization
function init() {
    renderProducts();
    setupEventListeners();
    updateFilterCounts();
}

// Render Products
function renderProducts() {
    // Filter
    let filtered = products.filter(product => {
        const brandMatch = state.filters.brands.length === 0 || state.filters.brands.includes(product.brand);
        const priceMatch = product.price <= state.filters.maxPrice;
        return brandMatch && priceMatch;
    });

    // Sort
    filtered.sort((a, b) => {
        if (state.sortBy === 'price-asc') return a.price - b.price;
        if (state.sortBy === 'price-desc') return b.price - a.price;
        if (state.sortBy === 'newest') return (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0);
        return 0; // featured (default order)
    });

    // Update Count
    visibleCount.textContent = filtered.length;

    // Render HTML
    productsGrid.innerHTML = filtered.map(product => `
        <div class="product-card">
            <div class="product-image">
                <img src="${product.image}" alt="${product.title}" loading="lazy">
            </div>
            <div class="product-info">
                <span class="product-brand">${product.brand}</span>
                <h3 class="product-title">${product.title}</h3>
                <div class="product-price">¥${product.price}</div>
            </div>
        </div>
    `).join('');
    
    // Empty State
    if (filtered.length === 0) {
        productsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #666;">
                没有找到匹配的产品，请尝试调整筛选条件。
            </div>
        `;
    }
}

// Event Listeners
function setupEventListeners() {
    // Brand Checkboxes
    brandFilters.forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                state.filters.brands.push(e.target.value);
            } else {
                state.filters.brands = state.filters.brands.filter(b => b !== e.target.value);
            }
            renderProducts();
        });
    });

    // Price Slider
    priceSlider.addEventListener('input', (e) => {
        const value = parseInt(e.target.value);
        state.filters.maxPrice = value;
        priceValue.textContent = `¥${value}`;
        renderProducts();
    });

    // Sort Select
    sortSelect.addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        renderProducts();
    });

    // Clear Filters
    clearFiltersBtn.addEventListener('click', () => {
        state.filters.brands = [];
        state.filters.maxPrice = 1000;
        
        // Reset UI
        brandFilters.forEach(cb => cb.checked = false);
        priceSlider.value = 1000;
        priceValue.textContent = '¥1000';
        
        renderProducts();
    });

    // Mobile Filter Toggle
    filterToggleBtn.addEventListener('click', () => {
        filtersSidebar.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    });

    // Mobile Apply Button (closes sidebar)
    mobileApplyBtn.addEventListener('click', () => {
        filtersSidebar.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close sidebar when clicking outside (simple implementation)
    document.addEventListener('click', (e) => {
        if (filtersSidebar.classList.contains('active') && 
            !filtersSidebar.contains(e.target) && 
            !filterToggleBtn.contains(e.target)) {
            filtersSidebar.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
}

function updateFilterCounts() {
    // In a real app, this would calculate counts based on available data
    // For now, static counts in HTML match the mock data roughly
}

// Run
document.addEventListener('DOMContentLoaded', init);
