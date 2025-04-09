import apiClient from './apiClient';

// Define interfaces
export interface Deck {
  id?: string;
  name: string;
  format: string;
  player_id: string;
  tournament_id: string;
  validation_status: string;
  validation_errors?: string[];
  main_deck: {name: string, quantity: number}[];
  sideboard: {name: string, quantity: number}[];
}

export interface DeckListResponse {
  decks: Deck[];
  total: number;
  page: number;
  limit: number;
}

// Deck API service
const DeckService = {
  // Get all decks with pagination
  getAllDecks: async (page = 1, limit = 20, format = '', player_id = '') => {
    const response = await apiClient.get('/decks', {
      params: { page, limit, format, player_id }
    });
    return response.data as DeckListResponse;
  },

  // Get deck by ID
  getDeckById: async (id: string) => {
    const response = await apiClient.get(`/decks/${id}`);
    return response.data as Deck;
  },

  // Create new deck
  createDeck: async (deckData: Deck) => {
    const response = await apiClient.post('/decks', deckData);
    return response.data;
  },

  // Update deck
  updateDeck: async (id: string, deckData: Partial<Deck>) => {
    const response = await apiClient.put(`/decks/${id}`, deckData);
    return response.data;
  },

  // Delete deck
  deleteDeck: async (id: string) => {
    const response = await apiClient.delete(`/decks/${id}`);
    return response.data;
  },

  // Validate deck
  validateDeck: async (id: string) => {
    const response = await apiClient.post(`/decks/${id}/validate`);
    return response.data;
  },

  // Import deck from text
  importDeckFromText: async (deckText: string, format: string, player_id: string, tournament_id: string, name: string) => {
    const response = await apiClient.post('/decks/import', {
      deck_text: deckText,
      format,
      player_id,
      tournament_id,
      name
    });
    return response.data;
  },

  // Export deck to text
  exportDeckToText: async (id: string) => {
    const response = await apiClient.get(`/decks/${id}/export`);
    return response.data;
  },

  // Get player decks
  getPlayerDecks: async (player_id: string) => {
    const response = await apiClient.get(`/players/${player_id}/decks`);
    return response.data;
  },

  // Get tournament decks
  getTournamentDecks: async (tournament_id: string) => {
    const response = await apiClient.get(`/tournaments/${tournament_id}/decks`);
    return response.data;
  }
};

export default DeckService;
