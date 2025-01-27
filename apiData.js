// apiData.js
import { catchError } from "./catchError.js";

export const apiData = {
  dataParsed: null,
  dataLoaded: false,

  async init() {
    if (this.dataLoaded) return;
    
    const [error, dataParsed] = await this.loadData();
    if (error) return console.error(error);

    this.dataParsed = dataParsed;
    this.dataLoaded = true;
  },

  async loadData() {
    const [error, data] = await catchError(fetch("./data/data.json"));
    if (error) return [error, null];

    const [errorJson, dataJson] = await catchError(data.json());
    return errorJson ? [errorJson, null] : [null, dataJson];
  },

  // Méthodes de filtrage mises à jour
  async filterByField(field, value) {
    await this.init();
    return this.dataParsed.filter(item => 
      item[field]?.toLowerCase().includes(value.toLowerCase())
    );
  },

  async filterByYear(year) {
    await this.init();
    return this.dataParsed.filter(item => {
      const validityYear = item.validity?.split(' ').pop();
      return validityYear === year;
    });
  },

  async filterByPriceRange(min, max) {
    await this.init();
    return this.dataParsed.filter(item => {
      const price = parseFloat(item.current_price);
      return price >= min && price <= max;
    });
  },

  async filterByPromotion(isPromotion) {
    await this.init();
    return this.dataParsed.filter(item => {
      const prev = parseFloat(item.previous_price);
      const curr = parseFloat(item.current_price);
      return (prev > curr) === isPromotion;
    });
  },

  // Méthodes conservées (champs existants dans le JSON)
  async searchByName(name) {
    return this.filterByField("name", name);
  },

  async filterByBrand(brand) {
    return this.filterByField("brand", brand);
  },

  async filterByStoreType(store) {
    return this.filterByField("store", store);
  },

  // Méthodes désactivées (champs manquants dans le JSON)
  /*
  async filterByCategory() {
    throw new Error("Non implémenté avec ce format de données");
  },

  async filterByAvailability() {
    throw new Error("Non implémenté avec ce format de données");
  },

  async filterByNewProducts() {
    throw new Error("Non implémenté avec ce format de données");
  }
  */
};