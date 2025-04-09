import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';

// Add missing Alert import
import { Alert } from 'react-bootstrap';

interface StandingsProps {}

interface Standing {
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

const Standings: React.FC<StandingsProps> = () => {
  const { id } = useParams<{ id: string }>();
  const [tournamentName, setTournamentName] = useState<string>('');
  const [standings, setStandings] = useState<Standing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockTournamentName = 'Friday Night Magic';
    
    const mockStandings: Standing[] = Array.from({ length: 16 }, (_, i) => ({
      rank: i + 1,
      player_id: `p${i + 1}`,
      player_name: `Player ${i + 1}`,
      matches_played: Math.min(3, Math.floor(Math.random() * 4)),
      match_points: Math.floor(Math.random() * 9),
      game_points: Math.floor(Math.random() * 6),
      match_win_percentage: Math.random(),
      game_win_percentage: Math.random(),
      opponents_match_win_percentage: Math.random(),
      opponents_game_win_percentage: Math.random(),
      active: Math.random() > 0.1
    }));
    
    // Sort by match points and other tiebreakers
    mockStandings.sort((a, b) => {
      if (a.match_points !== b.match_points) {
        return b.match_points - a.match_points;
      }
      if (a.opponents_match_win_percentage !== b.opponents_match_win_percentage) {
        return b.opponents_match_win_percentage - a.opponents_match_win_percentage;
      }
      if (a.game_win_percentage !== b.game_win_percentage) {
        return b.game_win_percentage - a.game_win_percentage;
      }
      return b.opponents_game_win_percentage - a.opponents_game_win_percentage;
    });
    
    // Update ranks
    mockStandings.forEach((standing, index) => {
      standing.rank = index + 1;
    });

    setTournamentName(mockTournamentName);
    setStandings(mockStandings);
    setLoading(false);
  }, [id]);

  const getRowClassName = (rank: number) => {
    if (rank === 1) return 'first-place';
    if (rank === 2) return 'second-place';
    if (rank === 3) return 'third-place';
    return '';
  };

  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        Error: {error}
      </Alert>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Standings: {tournamentName}</h1>
        <div>
          <Button variant="outline-primary" className="me-2">
            Print Standings
          </Button>
          <Link to={`/tournaments/${id}`} className="btn btn-outline-secondary">
            Back to Tournament
          </Link>
        </div>
      </div>

      <Card>
        <Card.Body>
          <Table responsive hover className="standings-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Player</th>
                <th>Match Points</th>
                <th>Matches</th>
                <th>Game Points</th>
                <th>OMW%</th>
                <th>GW%</th>
                <th>OGW%</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {standings.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center">No standings available</td>
                </tr>
              ) : (
                standings.map((standing) => (
                  <tr key={standing.player_id} className={getRowClassName(standing.rank)}>
                    <td>{standing.rank}</td>
                    <td>
                      <Link to={`/players/${standing.player_id}`}>{standing.player_name}</Link>
                    </td>
                    <td>{standing.match_points}</td>
                    <td>{standing.matches_played}</td>
                    <td>{standing.game_points}</td>
                    <td>{(standing.opponents_match_win_percentage * 100).toFixed(1)}%</td>
                    <td>{(standing.game_win_percentage * 100).toFixed(1)}%</td>
                    <td>{(standing.opponents_game_win_percentage * 100).toFixed(1)}%</td>
                    <td>
                      {standing.active ? (
                        <Badge bg="success">Active</Badge>
                      ) : (
                        <Badge bg="danger">Dropped</Badge>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      <div className="mt-4">
        <h5>Tiebreakers Explanation</h5>
        <ul>
          <li><strong>Match Points:</strong> 3 points for a win, 1 point for a draw, 0 points for a loss</li>
          <li><strong>OMW%:</strong> Opponents' Match Win Percentage</li>
          <li><strong>GW%:</strong> Game Win Percentage</li>
          <li><strong>OGW%:</strong> Opponents' Game Win Percentage</li>
        </ul>
      </div>
    </div>
  );
};

export default Standings;
