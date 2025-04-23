import apiClient from './apiClient';
import { Tournament, Match, Standing } from '../types';

// Tournament API service
const TournamentService = {
  // Get all tournaments with pagination
  getAllTournaments: async (page = 1, limit = 20, status = '') => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { page, limit, status }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching tournaments:', error);
      return { tournaments: [], total: 0, page, limit };
    }
  },

  // Get active tournaments
  getActiveTournaments: async () => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { status: 'active' }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching active tournaments:', error);
      return { tournaments: [] };
    }
  },

  // Get recent tournaments
  getRecentTournaments: async (limit = 5) => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { status: 'completed', limit, sort: 'date' }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent tournaments:', error);
      return { tournaments: [] };
    }
  },

  // Get tournament by ID
  getTournamentById: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament details:', error);
      throw error;
    }
  },

  // Create new tournament
  createTournament: async (tournamentData: Tournament) => {
    try {
      const response = await apiClient.post('/tournaments', tournamentData);
      return response.data;
    } catch (error) {
      console.error('Error creating tournament:', error);
      throw error;
    }
  },

  // Update tournament
  updateTournament: async (id: string, tournamentData: Partial<Tournament>) => {
    try {
      const response = await apiClient.put(`/tournaments/${id}`, tournamentData);
      return response.data;
    } catch (error) {
      console.error('Error updating tournament:', error);
      throw error;
    }
  },

  // Delete tournament
  deleteTournament: async (id: string) => {
    try {
      const response = await apiClient.delete(`/tournaments/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting tournament:', error);
      throw error;
    }
  },

  // Get tournament players
  getTournamentPlayers: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/players`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament players:', error);
      return [];
    }
  },

  // Register player
  registerPlayer: async (id: string, playerId: string) => {
    try {
      const response = await apiClient.post(`/tournaments/${id}/players`, { player_id: playerId });
      return response.data;
    } catch (error) {
      console.error('Error registering player:', error);
      throw error;
    }
  },

  // Drop player
  dropPlayer: async (id: string, playerId: string) => {
    try {
      const response = await apiClient.delete(`/tournaments/${id}/players/${playerId}`);
      return response.data;
    } catch (error) {
      console.error('Error dropping player:', error);
      throw error;
    }
  },

  // Reinstate player
  reinstatePlayer: async (id: string, playerId: string) => {
    try {
      const response = await apiClient.post(`/tournaments/${id}/players/${playerId}/reinstate`);
      return response.data;
    } catch (error) {
      console.error('Error reinstating player:', error);
      throw error;
    }
  },

  // Get tournament rounds
  getTournamentRounds: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/rounds`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament rounds:', error);
      return [];
    }
  },

  // Get round pairings
  getRoundPairings: async (id: string, round: number) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/rounds/${round}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching round pairings:', error);
      return [];
    }
  },

  // Create next round
  startNextRound: async (id: string) => {
    try {
      const response = await apiClient.post(`/tournaments/${id}/rounds/next`);
      return response.data;
    } catch (error) {
      console.error('Error creating next round:', error);
      throw error;
    }
  },

  // Get tournament standings
  getStandings: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/standings`);
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament standings:', error);
      return [];
    }
  },

  // Update standings
  updateStandings: async (id: string, standings: Standing[]) => {
    try {
      const response = await apiClient.put(`/tournaments/${id}/standings`, { standings });
      return response.data;
    } catch (error) {
      console.error('Error updating standings:', error);
      throw error;
    }
  },

  // Start tournament
  startTournament: async (id: string) => {
    try {
      const response = await apiClient.post(`/tournaments/${id}/start`);
      return response.data;
    } catch (error) {
      console.error('Error starting tournament:', error);
      throw error;
    }
  },

  // End tournament
  endTournament: async (id: string) => {
    try {
      const response = await apiClient.post(`/tournaments/${id}/end`);
      return response.data;
    } catch (error) {
      console.error('Error ending tournament:', error);
      throw error;
    }
  },

  // Get tournament matches
  getTournamentMatches: async (id: string, round?: number) => {
    try {
      const params = round ? { round } : {};
      const response = await apiClient.get(`/tournaments/${id}/matches`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching tournament matches:', error);
      return [];
    }
  }
};

export default TournamentService;