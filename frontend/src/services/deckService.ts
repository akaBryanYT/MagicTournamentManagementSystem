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
  main_deck: CardItem[];
  sideboard: CardItem[];
}

export interface CardItem {
  name: string;
  quantity: number;
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
    try {
      const response = await apiClient.get('/decks', {
        params: { page, limit, format, player_id }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching decks:', error);
      return { decks: [], total: 0, page, limit };
    }
  },

  // Get deck by ID
  getDeckById: async (id: string) => {
    try {
      const response = await apiClient.get(`/decks/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching deck:', error);
      throw error;
    }
  },

  // Create new deck
  createDeck: async (deckData: Partial<Deck>) => {
    try {
      // Make sure validation_status is included
      const completeData = {
        ...deckData,
        validation_status: deckData.validation_status || 'pending'
      };
      const response = await apiClient.post('/decks', completeData);
      return response.data;
    } catch (error) {
      console.error('Error creating deck:', error);
      throw error;
    }
  },

  // Update deck
  updateDeck: async (id: string, deckData: Partial<Deck>) => {
    try {
      const response = await apiClient.put(`/decks/${id}`, deckData);
      return response.data;
    } catch (error) {
      console.error('Error updating deck:', error);
      throw error;
    }
  },

  // Delete deck
  deleteDeck: async (id: string) => {
    try {
      const response = await apiClient.delete(`/decks/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting deck:', error);
      throw error;
    }
  },

  // Validate deck
  validateDeck: async (id: string, format: string) => {
    try {
      const response = await apiClient.post(`/decks/${id}/validate`, {
		format_name: format
	  });
      return response.data;
    } catch (error) {
      console.error('Error validating deck:', error);
      throw error;
    }
  },
    
  // Import deck from Moxfield URL
  importDeckFromMoxfield: async (playerId: string, tournamentId: string, moxfieldUrl: string, name?: string) => {
    try {
      const response = await apiClient.post('/decks/import', {
        player_id: playerId,
        tournament_id: tournamentId,
        moxfield_url: moxfieldUrl,
        name: name || 'Moxfield Deck'
      });
      return response.data;
    } catch (error) {
      console.error('Error importing deck from Moxfield:', error);
      throw error;
    }
  },
  
  // Import deck from text format
  importDeckFromText: async (playerId: string, tournamentId: string, deckText: string, format: string, name?: string) => {
    try {
      const response = await apiClient.post('/decks/import', {
        player_id: playerId,
        tournament_id: tournamentId,
        deck_text: deckText,
        format: format,
        name: name || 'Imported Deck'
      });
      return response.data;
    } catch (error) {
      console.error('Error importing deck from text:', error);
      throw error;
    }
  },

  // Export deck to text
  exportDeckToText: async (id: string) => {
    try {
      const response = await apiClient.get(`/decks/${id}/export`);
      return response.data;
    } catch (error) {
      console.error('Error exporting deck:', error);
      throw error;
    }
  },

  // Get player decks
  getPlayerDecks: async (player_id: string) => {
    try {
      const response = await apiClient.get(`/players/${player_id}/decks`);
      return response.data;
    } catch (error) {
      console.error('Error fetching player decks:', error);
      return [];
    }
  },

  // Get tournament decks
  getTournamentDecks: async (tournament_id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${tournament_id}/decks`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament decks:', error);
      return [];
    }
  }
};

export default DeckService;