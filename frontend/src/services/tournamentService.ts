import apiClient from './apiClient';

// Define interfaces
export interface Tournament {
  id?: string;
  name: string;
  format: string;
  structure: string;
  date: string;
  location: string;
  status: string;
  rounds: number;
  current_round: number;
  time_limit: number;
  structure_config: {
    allow_intentional_draws?: boolean;
    use_seeds_for_byes?: boolean;
    seeded?: boolean;
    third_place_match?: boolean;
    grand_finals_modifier?: string;
  };
  format_config: any;
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

export interface Player {
  id: string;
  name: string;
  email: string;
  active: boolean;
}

export interface Standing {
  id: string;
  player_id: string;
  player_name: string;
  rank: number;
  matches_played: number;
  match_points: number;
  game_points: number;
  match_win_percentage: number;
  game_win_percentage: number;
  opponents_match_win_percentage: number;
  opponents_game_win_percentage: number;
  active: boolean;
}

export interface Match {
  id: string;
  tournament_id: string;
  round: number;
  bracket?: string;
  bracket_position?: number;
  table_number: number;
  player1_id: string;
  player1_name: string;
  player2_id?: string;
  player2_name?: string;
  player1_wins: number;
  player2_wins: number;
  draws: number;
  status: string;
  result: string;
  next_match?: number;
  winners_next_match?: number;
  losers_next_match?: number;
}

export interface MatchResult {
  player1_wins: number;
  player2_wins: number;
  draws: number;
}

// Tournament API service
const TournamentService = {
  // Get all tournaments with pagination
  getAllTournaments: async (page = 1, limit = 20, status = '') => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { page, limit, status }
      });
      return response.data as TournamentListResponse;
    } catch (error) {
      console.error('Error fetching tournaments:', error);
      throw error;
    }
  },

  // Get active tournaments
  getActiveTournaments: async () => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { status: 'active' }
      });
      return response.data.tournaments as Tournament[];
    } catch (error) {
      console.error('Error fetching active tournaments:', error);
      throw error;
    }
  },

  // Get recent tournaments
  getRecentTournaments: async (limit = 5) => {
    try {
      const response = await apiClient.get('/tournaments', {
        params: { status: 'completed', limit, sort: 'date' }
      });
      return response.data.tournaments as Tournament[];
    } catch (error) {
      console.error('Error fetching recent tournaments:', error);
      throw error;
    }
  },

  // Get tournament by ID
  getTournamentById: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}`);
      return response.data as Tournament;
    } catch (error) {
      console.error('Error fetching tournament details:', error);
      throw error;
    }
  },

  // Create new tournament
  createTournament: async (tournamentData: Tournament) => {
    try {
      // Transform frontend data to backend format
      const apiData = {
        name: tournamentData.name,
        format: tournamentData.format,
        structure: tournamentData.structure,
        date: tournamentData.date,
        location: tournamentData.location,
        rounds: tournamentData.rounds || 0,
        time_limit: tournamentData.time_limit,
        structure_config: {
          allow_intentional_draws: tournamentData.structure_config.allow_intentional_draws,
          use_seeds_for_byes: tournamentData.structure_config.use_seeds_for_byes,
          seeded: tournamentData.structure_config.seeded,
          third_place_match: tournamentData.structure_config.third_place_match,
          grand_finals_modifier: tournamentData.structure_config.grand_finals_modifier
        },
        format_config: tournamentData.format_config,
        tiebreakers: {
          match_points: tournamentData.tiebreakers.match_points,
          opponents_match_win_percentage: tournamentData.tiebreakers.opponents_match_win_percentage,
          game_win_percentage: tournamentData.tiebreakers.game_win_percentage,
          opponents_game_win_percentage: tournamentData.tiebreakers.opponents_game_win_percentage
        }
      };

      const response = await apiClient.post('/tournaments', apiData);
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
      return response.data as Player[];
    } catch (error) {
      console.error('Error fetching tournament players:', error);
      throw error;
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
      throw error;
    }
  },

  // Get round pairings
  getRoundPairings: async (id: string, round: number) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/rounds/${round}`);
      return response.data as Match[];
    } catch (error) {
      console.error('Error fetching round pairings:', error);
      throw error;
    }
  },

  // Get current round pairings
  getCurrentPairings: async (id: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/pairings`);
      return response.data as Match[];
    } catch (error) {
      console.error('Error fetching current pairings:', error);
      throw error;
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
      return response.data as Standing[];
    } catch (error) {
      console.error('Error fetching tournament standings:', error);
      throw error;
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

  // Generate tournament reports
  generateReport: async (id: string, reportType: string) => {
    try {
      const response = await apiClient.get(`/tournaments/${id}/reports/${reportType}`);
      return response.data;
    } catch (error) {
      console.error('Error generating tournament report:', error);
      throw error;
    }
  },

  // Get tournament matches
  getTournamentMatches: async (id: string, round?: number) => {
    try {
      const params = round ? { round } : {};
      const response = await apiClient.get(`/tournaments/${id}/matches`, { params });
      return response.data as Match[];
    } catch (error) {
      console.error('Error fetching tournament matches:', error);
      throw error;
    }
  },
  
  // Update match result
  updateMatchResult: async (matchId: string, result: MatchResult) => {
    try {
      const response = await apiClient.post(`/matches/${matchId}/result`, result);
      return response.data;
    } catch (error) {
      console.error('Error updating match result:', error);
      throw error;
    }
  },
  
  // Mark match as draw
  drawMatch: async (matchId: string) => {
    try {
      const response = await apiClient.post(`/matches/${matchId}/draw`);
      return response.data;
    } catch (error) {
      console.error('Error marking match as draw:', error);
      throw error;
    }
  }
};

export default TournamentService;