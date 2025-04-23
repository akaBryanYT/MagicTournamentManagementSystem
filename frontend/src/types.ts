// src/types.ts
export interface Tournament {
  id: string | undefined;  // Changed from just string to accept undefined
  name: string;
  format: string;
  date: string;
  status: string;
  player_count?: number;
  playerCount?: number;
  current_round: number;
  rounds: number;
  structure?: string;
  location?: string;
  time_limit?: number;
  structure_config?: {
    allow_intentional_draws?: boolean;
    use_seeds_for_byes?: boolean;
    seeded?: boolean;
    third_place_match?: boolean;
    grand_finals_modifier?: string;
  };
  format_config?: {
    podSize?: number;
    packsPerPlayer?: number;
    pointSystem?: string;  // Added missing property
  };
  tiebreakers?: {
    match_points: boolean;
    opponents_match_win_percentage: boolean;
    game_win_percentage: boolean;
    opponents_game_win_percentage: boolean;
  };
}

export interface Player {
  id: string;
  name: string;
  email: string;
  phone?: string;
  dci_number?: string;
  active: boolean;
  tournamentCount?: number;  // Made optional
}

export interface Match {
  id: string;
  tournament_id: string;
  tournament_name?: string;
  round: number;
  table_number: number;
  player1_id: string;
  player1_name: string;
  player2_id?: string;  // Made optional to match service
  player2_name?: string;  // Made optional to match service
  player1_wins: number;
  player2_wins: number;
  draws: number;
  result: string;
  status: string;
  bracket?: string;
  bracket_position?: number;
}

export interface Standing {
  id: string;
  rank: number;
  player_id: string;
  player_name: string;
  matches_played: number;
  match_points: number;
  game_points: number;
  match_win_percentage: number;
  game_win_percentage: number;
  opponents_match_win_percentage: number;
  opponents_game_win_percentage: number;
  active: boolean;
}

export interface Deck {
  id?: string;
  name: string;
  format: string;
  player_id: string;
  player_name?: string;
  tournament_id: string;
  tournament_name?: string;
  validation_status: string;
  validation_errors?: string[];
  main_deck: CardItem[];
  sideboard: CardItem[];
}

export interface CardItem {
  name: string;
  quantity: number;
}