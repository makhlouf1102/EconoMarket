import { catchError } from "./catchError.js";
import { apiData } from "./apiData.js";

let allProducts = [];

window.onload = async function () {
    try {
        await apiData.init();
        allProducts = apiData.dataParsed || [];

        // Initialize price inputs
        const prices = allProducts
            .map(p => parseFloat(p.price_text || 0))
            .filter(price => !isNaN(price));
        
        const maxProductPrice = prices.length ? Math.ceil(Math.max(...prices)) : 100;
        document.getElementById('maxPriceInput').placeholder = maxProductPrice;
        document.getElementById('maxPriceInput').max = maxProductPrice;

        // Set up event listeners
        document.getElementById('minPriceInput').addEventListener('input', applyFilters);
        document.getElementById('maxPriceInput').addEventListener('input', applyFilters);

        populateCategoryFilter();
        populateBrandFilter();
        displayProducts(allProducts);

    } catch (error) {
        console.error('Initialization error:', error);
    }
};

function populateCategoryFilter() {
    const categorySet = new Set();
    allProducts.forEach(prod => {
        if (Array.isArray(prod.categories)) {
            prod.categories.forEach(cat => categorySet.add(cat));
        }
    });
    const categoryFilter = document.getElementById('categoryFilter');
    while (categoryFilter.options.length > 1) categoryFilter.remove(1);
    
    [...categorySet].sort((a, b) => a.localeCompare(b)).forEach(category => {
        const option = new Option(category, category);
        categoryFilter.add(option);
    });
}

function populateBrandFilter() {
    const brandSet = new Set();
    allProducts.forEach(prod => brandSet.add(prod.brand));
    const brandFilter = document.getElementById('brandFilter');
    while (brandFilter.options.length > 1) brandFilter.remove(1);
    
    [...brandSet].sort((a, b) => a.localeCompare(b)).forEach(brand => {
        const option = new Option(brand, brand);
        brandFilter.add(option);
    });
}

function displayProducts(productArray) {
    const productList = document.getElementById("productList");
    productList.innerHTML = "";

    productArray.forEach(product => {
        const li = document.createElement("li");
        li.className = "product-item";

        // Product Image
        const imgDiv = document.createElement("div");
        imgDiv.className = "product-image";
        const img = new Image();
        img.src = product.images?.[0] || product.image_url || "placeholder.jpg";
        img.alt = product.name;
        imgDiv.appendChild(img);

        // Product Info
        const infoDiv = document.createElement("div");
        infoDiv.className = "product-info";

        const nameDiv = document.createElement("div");
        nameDiv.className = "product-name";
        nameDiv.textContent = product.name;

        // Store Info
        const storeDiv = document.createElement("div");
        storeDiv.className = "store-container";
        const storeLogo = new Image();
        storeLogo.className = "store-logo";
        const storeName = product.store?.replace(/\s+/g, '_') || 'default-store';
        storeLogo.src = `images/${storeName}.png`;
        storeLogo.alt = `${product.store || 'Unknown'} logo`;
        
        const storeNameSpan = document.createElement("span");
        storeNameSpan.className = "product-store";
        storeNameSpan.textContent = product.store || "N/A";
        
        storeDiv.append(storeLogo, storeNameSpan);

        // Product Details
        const detailsDiv = document.createElement("div");
        detailsDiv.className = "product-details";
        const categories = Array.isArray(product.categories) 
            ? product.categories.join(", ") 
            : "N/A";
        detailsDiv.innerHTML = `Category: ${categories}<br>Valid: ${product.valid_from || "N/A"} - ${product.valid_to || "N/A"}`;

        // Price Display
        const priceDiv = document.createElement("div");
        priceDiv.className = "product-price";
        priceDiv.textContent = product.price_text 
            ? `$${parseFloat(product.price_text).toFixed(2)}`
            : "$--";

        // Assemble elements
        infoDiv.append(nameDiv, storeDiv, detailsDiv);
        li.append(imgDiv, infoDiv, priceDiv);
        productList.appendChild(li);
    });
}

window.applyFilters = async function applyFilters() {
    try {
        if (!apiData.dataLoaded) {
            await apiData.init();
            allProducts = apiData.dataParsed || [];
        }

        let filtered = [...allProducts];
        const minPrice = parseFloat(document.getElementById('minPriceInput').value) || 0;
        const maxPrice = parseFloat(document.getElementById('maxPriceInput').value) || Infinity;
        const nameValue = document.getElementById('nameFilter').value.trim().toLowerCase();
        const categoryValue = document.getElementById('categoryFilter').value;
        const brandValue = document.getElementById('brandFilter').value;

        filtered = filtered.filter(product => {
            // Name filter
            if (nameValue && !product.name?.toLowerCase().includes(nameValue)) return false;
            
            // Category filter
            if (categoryValue && !product.categories?.includes(categoryValue)) return false;
            
            // Price filter
            const price = parseFloat(product.price_text || 0);
            if (isNaN(price) || price < minPrice || price > maxPrice) return false;
            
            // Brand filter
            if (brandValue && product.brand !== brandValue) return false;

            return true;
        });

        displayProducts(filtered);

    } catch (error) {
        console.error('Filtering error:', error);
    }
};