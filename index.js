import { catchError } from "./catchError.js";
import { apiData } from "./apiData.js";

let allProducts = [];

window.onload = async function () {
    try {
        await apiData.init();
        allProducts = apiData.dataParsed || [];

        // Initialize price inputs
        const prices = allProducts
            .map(p => parseFloat(p.current_price || 0))
            .filter(price => !isNaN(price));
        
        const maxProductPrice = prices.length ? Math.ceil(Math.max(...prices)) : 100;
        document.getElementById('maxPriceInput').placeholder = maxProductPrice;
        document.getElementById('maxPriceInput').max = maxProductPrice;

        // Set up event listeners
        document.getElementById('minPriceInput').addEventListener('input', applyFilters);
        document.getElementById('maxPriceInput').addEventListener('input', applyFilters);

        populateBrandFilter();
        displayProducts(allProducts);

    } catch (error) {
        console.error('Initialization error:', error);
    }
};

function populateBrandFilter() {
    const brandSet = new Set(allProducts.map(prod => prod.brand).filter(Boolean));
    const brandFilter = document.getElementById('brandFilter');
    
    // Reset filter options
    brandFilter.innerHTML = '<option value="">Toutes les marques</option>';
    
    [...brandSet].sort((a, b) => a.localeCompare(b)).forEach(brand => {
        brandFilter.add(new Option(brand, brand));
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
        img.src = product.image_url || "placeholder.jpg";
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
        const storeName = (product.store || 'default-store').replace(/\s+/g, '_');
        // RELPLACE WHITESPACE WITH UNDERSCORES
        if (storeName === 'SUPER C') {
            storeName = 'SUPER_C';
        }
        storeLogo.src = `images/${storeName}.png`;
        storeLogo.alt = `${product.store || 'Unknown'} logo`;
        
        const storeNameSpan = document.createElement("span");
        storeNameSpan.className = "product-store";
        storeNameSpan.textContent = product.store || "N/A";
        
        storeDiv.append(storeLogo, storeNameSpan);

        // Product Details
        const detailsDiv = document.createElement("div");
        detailsDiv.className = "product-details";
        detailsDiv.innerHTML = `
            ${product.validity ? `Validité: ${product.validity}` : ''}<br>
            ${product.price_per_item ? `Prix unitaire: ${product.price_per_item}` : ''}
        `;

        // Price Display
        const priceDiv = document.createElement("div");
        priceDiv.className = "product-price";
        
        const currentPrice = parseFloat(product.current_price);
        const previousPrice = parseFloat(product.previous_price);
        const hasDiscount = previousPrice > currentPrice;

        priceDiv.innerHTML = `
            ${hasDiscount ? `<span class="old-price">${previousPrice.toFixed(2)}$</span>` : ''}
            <span class="${hasDiscount ? 'discount-price' : ''}">${currentPrice.toFixed(2)}$</span>
        `;

        // Assemble elements
        infoDiv.append(nameDiv, storeDiv, detailsDiv);
        li.append(imgDiv, infoDiv, priceDiv);
        productList.appendChild(li);
    });
}

function sortProducts(products, sortBy) {
    return [...products].sort((a, b) => {
        const priceA = parseFloat(a.current_price);
        const priceB = parseFloat(b.current_price);
        
        switch(sortBy) {
            case 'price_asc':
                return priceA - priceB;
            case 'price_desc':
                return priceB - priceA;
            case 'name_asc':
                return a.name.localeCompare(b.name);
            case 'name_desc':
                return b.name.localeCompare(a.name);
            default:
                return 0;
        }
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
        const brandValue = document.getElementById('brandFilter').value;
        const sortBy = document.getElementById('sortSelect').value;

        filtered = filtered.filter(product => {
            // Name filter
            if (nameValue && !product.name?.toLowerCase().includes(nameValue)) return false;
            
            // Price filter
            const price = parseFloat(product.current_price || 0);
            if (isNaN(price) || price < minPrice || price > maxPrice) return false;
            
            // Brand filter
            if (brandValue && product.brand !== brandValue) return false;

            return true;
        });

        // Apply sorting
        filtered = sortProducts(filtered, sortBy);

        displayProducts(filtered);

    } catch (error) {
        console.error('Filtering error:', error);
    }
};