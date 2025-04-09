import apiClient from './apiClient';

// Define interfaces
export interface Tournament {
  id?: string;
  name: string;
  format: string;
  date: string;
  location: string;
  status: string;
  rounds: number;
  current_round: number;
  player_count: number;
  time_limit: number;
  allow_intentional_draws: boolean;
  tiebreakers: {
    match_points: boolean;
    opponents_match_win_percentage: boolean;
    game_win_percentage: boolean;
    opponents_game_win_percentage: boolean;
  };
}

export interface TournamentListResponse {
  tournaments: Tournament[];
  total: number;
  page: number;
  limit: number;
}

// Tournament API service
const TournamentService = {
  // Get all tournaments with pagination
  getAllTournaments: async (page = 1, limit = 20, status = '') => {
    const response = await apiClient.get('/tournaments', {
      params: { page, limit, status }
    });
    return response.data as TournamentListResponse;
  },

  // Get tournament by ID
  getTournamentById: async (id: string) => {
    const response = await apiClient.get(`/tournaments/${id}`);
    return response.data as Tournament;
  },

  // Create new tournament
  createTournament: async (tournamentData: Tournament) => {
    const response = await apiClient.post('/tournaments', tournamentData);
    return response.data;
  },

  // Update tournament
  updateTournament: async (id: string, tournamentData: Partial<Tournament>) => {
    const response = await apiClient.put(`/tournaments/${id}`, tournamentData);
    return response.data;
  },

  // Delete tournament
  deleteTournament: async (id: string) => {
    const response = await apiClient.delete(`/tournaments/${id}`);
    return response.data;
  },

  // Get tournament players
  getTournamentPlayers: async (id: string) => {
    const response = await apiClient.get(`/tournaments/${id}/players`);
    return response.data;
  },

  // Register player for tournament
  registerPlayer: async (id: string, playerId: string) => {
    const response = await apiClient.post(`/tournaments/${id}/players`, { player_id: playerId });
    return response.data;
  },

  // Drop player from tournament
  dropPlayer: async (id: string, playerId: string) => {
    const response = await apiClient.delete(`/tournaments/${id}/players/${playerId}`);
    return response.data;
  },

  // Get tournament pairings for current round
  getCurrentPairings: async (id: string) => {
    const response = await apiClient.get(`/tournaments/${id}/pairings`);
    return response.data;
  },

  // Get pairings for specific round
  getRoundPairings: async (id: string, round: number) => {
    const response = await apiClient.get(`/tournaments/${id}/pairings/${round}`);
    return response.data;
  },

  // Get tournament standings
  getStandings: async (id: string) => {
    const response = await apiClient.get(`/tournaments/${id}/standings`);
    return response.data;
  },

  // Start tournament
  startTournament: async (id: string) => {
    const response = await apiClient.post(`/tournaments/${id}/start`);
    return response.data;
  },

  // End tournament
  endTournament: async (id: string) => {
    const response = await apiClient.post(`/tournaments/${id}/end`);
    return response.data;
  },

  // Start next round
  startNextRound: async (id: string) => {
    const response = await apiClient.post(`/tournaments/${id}/next-round`);
    return response.data;
  },

  // Get tournament matches
  getTournamentMatches: async (id: string, round?: number) => {
    const params = round ? { round } : {};
    const response = await apiClient.get(`/tournaments/${id}/matches`, { params });
    return response.data;
  }
};

export default TournamentService;
