import apiClient from './apiClient';

// Define interfaces
export interface Card {
  id?: string;
  name: string;
  set_code: string;
  collector_number: string;
  mana_cost?: string;
  type_line: string;
  oracle_text?: string;
  power?: string;
  toughness?: string;
  colors?: string[];
  color_identity?: string[];
  legalities: Record<string, string>;
  rarity: string;
  image_uri?: string;
}

export interface CardListResponse {
  cards: Card[];
  total: number;
  page: number;
  limit: number;
}

// Card API service
const CardService = {
  // Get all cards with pagination
  getAllCards: async (page = 1, limit = 50, search = '') => {
    const response = await apiClient.get('/cards', {
      params: { page, limit, search }
    });
    return response.data as CardListResponse;
  },

  // Get card by ID
  getCardById: async (id: string) => {
    const response = await apiClient.get(`/cards/${id}`);
    return response.data as Card;
  },

  // Search cards by name
  searchCardsByName: async (name: string, limit = 20) => {
    const response = await apiClient.get('/cards/search', {
      params: { name, limit }
    });
    return response.data;
  },

  // Get cards by set
  getCardsBySet: async (setCode: string) => {
    const response = await apiClient.get(`/cards/set/${setCode}`);
    return response.data;
  },

  // Get cards by format
  getCardsByFormat: async (format: string) => {
    const response = await apiClient.get(`/cards/format/${format}`);
    return response.data;
  },

  // Check card legality in a format
  checkCardLegality: async (cardName: string, format: string) => {
    const response = await apiClient.get('/cards/legality', {
      params: { card: cardName, format }
    });
    return response.data;
  },

  // Batch import cards
  batchImportCards: async (cardsData: Card[]) => {
    const response = await apiClient.post('/cards/batch', { cards: cardsData });
    return response.data;
  }
};

export default CardService;
