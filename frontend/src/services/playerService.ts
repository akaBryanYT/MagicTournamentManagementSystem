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
    const response = await apiClient.get('/players', {
      params: { page, limit, search }
    });
    return response.data as PlayerListResponse;
  },

  // Get player by ID
  getPlayerById: async (id: string) => {
    const response = await apiClient.get(`/players/${id}`);
    return response.data as Player;
  },

  // Create new player
  createPlayer: async (playerData: Player) => {
    const response = await apiClient.post('/players', playerData);
    return response.data;
  },

  // Update player
  updatePlayer: async (id: string, playerData: Partial<Player>) => {
    const response = await apiClient.put(`/players/${id}`, playerData);
    return response.data;
  },

  // Delete player
  deletePlayer: async (id: string) => {
    const response = await apiClient.delete(`/players/${id}`);
    return response.data;
  },

  // Get player tournament history
  getPlayerTournaments: async (id: string) => {
    const response = await apiClient.get(`/players/${id}/tournaments`);
    return response.data;
  },

  // Get player decks
  getPlayerDecks: async (id: string) => {
    const response = await apiClient.get(`/players/${id}/decks`);
    return response.data;
  },

  // Activate/deactivate player
  togglePlayerStatus: async (id: string, active: boolean) => {
    const response = await apiClient.patch(`/players/${id}/status`, { active });
    return response.data;
  }
};

export default PlayerService;
