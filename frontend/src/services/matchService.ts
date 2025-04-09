import apiClient from './apiClient';

// Define interfaces
export interface Match {
  id?: string;
  tournament_id: string;
  round: number;
  table_number: number;
  player1_id: string;
  player2_id: string;
  player1_wins: number;
  player2_wins: number;
  draws: number;
  result: string;
  status: string;
}

export interface MatchResult {
  player1_wins: number;
  player2_wins: number;
  draws: number;
}

export interface MatchListResponse {
  matches: Match[];
  total: number;
  page: number;
  limit: number;
}

// Match API service
const MatchService = {
  // Get all matches with pagination
  getAllMatches: async (page = 1, limit = 20, tournament_id = '', round = 0) => {
    const response = await apiClient.get('/matches', {
      params: { page, limit, tournament_id, round }
    });
    return response.data as MatchListResponse;
  },

  // Get match by ID
  getMatchById: async (id: string) => {
    const response = await apiClient.get(`/matches/${id}`);
    return response.data as Match;
  },

  // Submit match result
  submitResult: async (id: string, result: MatchResult) => {
    const response = await apiClient.post(`/matches/${id}/result`, result);
    return response.data;
  },

  // Submit intentional draw
  submitIntentionalDraw: async (id: string) => {
    const response = await apiClient.post(`/matches/${id}/intentional-draw`);
    return response.data;
  },

  // Get tournament matches for a specific round
  getTournamentRoundMatches: async (tournament_id: string, round: number) => {
    const response = await apiClient.get(`/tournaments/${tournament_id}/rounds/${round}/matches`);
    return response.data;
  },

  // Get player match history
  getPlayerMatches: async (player_id: string, tournament_id = '') => {
    const params = tournament_id ? { tournament_id } : {};
    const response = await apiClient.get(`/players/${player_id}/matches`, { params });
    return response.data;
  },

  // Get match slip (for printing)
  getMatchSlip: async (id: string) => {
    const response = await apiClient.get(`/matches/${id}/slip`);
    return response.data;
  }
};

export default MatchService;
