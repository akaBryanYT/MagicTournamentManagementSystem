import apiClient from './apiClient';

// Define interfaces
export interface Player {
  id?: string;
  name: string;
  email: string;
  phone?: string;
  dci_number?: string;
  active: boolean;
}

export interface PlayerListResponse {
  players: Player[];
  total: number;
  page: number;
  limit: number;
}

// Player API service
const PlayerService = {
  // Get all players with pagination
  getAllPlayers: async (page = 1, limit = 20, search = '') => {
    try {
      const response = await apiClient.get('/players', {
        params: { page, limit, search }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching players:', error);
      return { players: [], total: 0, page, limit };
    }
  },

  // Get player by ID
  getPlayerById: async (id: string) => {
    try {
      const response = await apiClient.get(`/players/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching player details:', error);
      throw error;
    }
  },

  // Create new player
  createPlayer: async (playerData: Player) => {
    try {
      const response = await apiClient.post('/players', playerData);
      return response.data;
    } catch (error) {
      console.error('Error creating player:', error);
      throw error;
    }
  },

  // Update player
  updatePlayer: async (id: string, playerData: Partial<Player>) => {
    try {
      const response = await apiClient.put(`/players/${id}`, playerData);
      return response.data;
    } catch (error) {
      console.error('Error updating player:', error);
      throw error;
    }
  },

  // Delete player
  deletePlayer: async (id: string) => {
    try {
      const response = await apiClient.delete(`/players/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting player:', error);
      throw error;
    }
  },

  // Get player tournament history
  getPlayerTournaments: async (id: string) => {
    try {
      const response = await apiClient.get(`/players/${id}/tournaments`);
      return response.data;
    } catch (error) {
      console.error('Error fetching player tournaments:', error);
      return [];
    }
  },

  // Get player decks
  getPlayerDecks: async (id: string) => {
    try {
      const response = await apiClient.get(`/players/${id}/decks`);
      return response.data;
    } catch (error) {
      console.error('Error fetching player decks:', error);
      return [];
    }
  },

  // Activate/deactivate player
  togglePlayerStatus: async (id: string, active: boolean) => {
    try {
      const response = await apiClient.patch(`/players/${id}/status`, { active });
      return response.data;
    } catch (error) {
      console.error('Error toggling player status:', error);
      throw error;
    }
  },

  // Search players
  searchPlayers: async (query: string) => {
    try {
      const response = await apiClient.get('/players/search', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching players:', error);
      return [];
    }
  }
};

export default PlayerService;