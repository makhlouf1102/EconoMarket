import { catchError } from "./catchError.js";
import { apiData } from "./apiData.js";

let allProducts = [];

window.onload = async function () {
    try {
        await apiData.init();
        allProducts = apiData.dataParsed || [];

        // Initialize price inputs
        const prices = allProducts
            .map(p => parseFloat((p.current_price || "0").replace(",", ".")))
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
    brandFilter.textContent = '';

    const defaultOption = document.createElement('option');
    defaultOption.value = "";
    defaultOption.textContent = "Toutes les marques";
    brandFilter.appendChild(defaultOption);

    [...brandSet].sort((a, b) => a.localeCompare(b)).forEach(brand => {
        const option = document.createElement('option');
        option.value = brand;
        option.textContent = brand;
        brandFilter.appendChild(option);
    });
}

function displayProducts(productArray) {
    const productList = document.getElementById("productList");
    productList.textContent = "";

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
        let storeName = (product.store || 'default-store').replace(/\s+/g, '_');
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

        if (product.validity) {
            const validitySpan = document.createElement("span");
            validitySpan.textContent = `Validité: ${product.validity}`;
            detailsDiv.appendChild(validitySpan);
        }

        if (product.price_per_item) {
            const unitPriceSpan = document.createElement("span");
            unitPriceSpan.textContent = `Prix unitaire: ${product.price_per_item}`;
            detailsDiv.appendChild(unitPriceSpan);
        }

        // Price Display
        const priceDiv = document.createElement("div");
        priceDiv.className = "product-price";

        const currentPrice = parseFloat((product.current_price || "0").replace(",", ".")) || 0;
        const previousPrice = parseFloat((product.previous_price || "0").replace(",", ".")) || 0;
        const hasDiscount = previousPrice > currentPrice;

        if (hasDiscount) {
            const oldPriceSpan = document.createElement("span");
            oldPriceSpan.className = "old-price";
            oldPriceSpan.textContent = `${previousPrice.toFixed(2)}$`;
            priceDiv.appendChild(oldPriceSpan);
        }

        const currentPriceSpan = document.createElement("span");
        currentPriceSpan.className = hasDiscount ? "discount-price" : "";
        currentPriceSpan.textContent = `${currentPrice.toFixed(2)}$`;
        priceDiv.appendChild(currentPriceSpan);

        // Assemble elements
        infoDiv.append(nameDiv, storeDiv, detailsDiv);
        li.append(imgDiv, infoDiv, priceDiv);
        productList.appendChild(li);
    });
}

function sortProducts(products, sortBy) {
    return [...products].sort((a, b) => {
        const priceA = parseFloat((a.current_price || "0").replace(",", "."));
        const priceB = parseFloat((b.current_price || "0").replace(",", "."));

        switch (sortBy) {
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
            const price = parseFloat((product.current_price || "0").replace(",", "."));
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