// apiData.js
import { catchError } from "./catchError.js";

export const apiData = {
  dataParsed: null,
  dataLoaded: false,

  async init() {
    if (this.dataLoaded) {
      return;
    }

    const [error, dataParsed] = await this.loadData();
    if (error) {
      console.error(error);
      return;
    }

    this.dataParsed = dataParsed;
    this.dataLoaded = true;
  },

  async loadData() {
    // Load from local JSON
    const [error, data] = await catchError(fetch("./data/data.json"));
    if (error) {
      console.error(error);
      return [null, new Error("Failed to load JSON data")];
    }

    const [errorJson, dataJson] = await catchError(data.json());
    if (errorJson) {
      console.error(errorJson);
      return [null, new Error("Failed to parse JSON data")];
    }

    return [null, dataJson];
  },

  async filterByField(field, value) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      return item[field] && String(item[field]).toLowerCase().includes(value.toLowerCase());
    });
  },

  async filterByYear(year) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      return item.valid_from && item.valid_from.startsWith(year);
    });
  },

  async filterByText(text) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      return JSON.stringify(item).toLowerCase().includes(text.toLowerCase());
    });
  },

  async searchByName(name) {
    return this.filterByField("name", name);
  },

  async filterByCategory(category) {
    return this.filterByField("categories", category);
  },

  async filterByPriceRange(minPrice, maxPrice) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      const price = parseFloat(item.price_text);
      return !isNaN(price) && price >= minPrice && price <= maxPrice;
    });
  },

  async filterByBrand(brand) {
    return this.filterByField("brand", brand);
  },

  async filterByAvailability(status) {
    return this.filterByField("status", status);
  },

  async filterByPromotion(isPromotion) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      return Boolean(item.promotion) === isPromotion;
    });
  },

  async filterByStoreType(storeType) {
    return this.filterByField("store", storeType);
  },

  async filterByNewProducts(isNew) {
    if (!this.dataLoaded) {
      await this.init();
    }
    return this.dataParsed.filter((item) => {
      return Boolean(item.is_new_product) === isNew;
    });
  }
};
