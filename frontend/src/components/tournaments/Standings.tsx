// src/components/tournaments/Standings.tsx
import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col, Alert } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';
import { Standing as StandingType } from '../../types';

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
    const fetchStandings = async () => {
      try {
        setLoading(true);
        // Fetch tournament details
        const tournamentData = await TournamentService.getTournamentById(id!);
        setTournamentName(tournamentData.name);
        
        // Fetch standings
        const standingsData = await TournamentService.getStandings(id!);
        setStandings(standingsData as unknown as Standing[]);
      } catch (err) {
        console.error("Error fetching standings:", err);
        setError("Failed to load standings");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchStandings();
    }
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
          <Button variant="outline-secondary" size="sm" onClick={() => {
            const printWindow = window.open('', '_blank');
            
            if (printWindow) {
              printWindow.document.write(`
                <html>
                  <head>
                    <title>Standings: ${tournamentName}</title>
                    <style>
                      body { font-family: Arial, sans-serif; }
                      table { border-collapse: collapse; width: 100%; }
                      th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                      th { background-color: #f2f2f2; }
                      .first-place { background-color: rgba(255, 215, 0, 0.2); }
                      .second-place { background-color: rgba(192, 192, 192, 0.2); }
                      .third-place { background-color: rgba(205, 127, 50, 0.2); }
                    </style>
                  </head>
                  <body>
                    <h1>Standings: ${tournamentName}</h1>
                    <table>
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
                        ${standings.map(standing => `
                          <tr class="${standing.rank === 1 ? 'first-place' : 
                                      standing.rank === 2 ? 'second-place' : 
                                      standing.rank === 3 ? 'third-place' : ''}">
                            <td>${standing.rank}</td>
                            <td>${standing.player_name}</td>
                            <td>${standing.match_points}</td>
                            <td>${standing.matches_played}</td>
                            <td>${standing.game_points}</td>
                            <td>${(standing.opponents_match_win_percentage * 100).toFixed(1)}%</td>
                            <td>${(standing.game_win_percentage * 100).toFixed(1)}%</td>
                            <td>${(standing.opponents_game_win_percentage * 100).toFixed(1)}%</td>
                            <td>${standing.active ? 'Active' : 'Dropped'}</td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                  </body>
                </html>
              `);
              printWindow.document.close();
              printWindow.focus();
              printWindow.print();
              printWindow.close();
            }
          }}>
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