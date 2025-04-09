import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';

interface PairingsProps {}

interface Pairing {
  match_id: string;
  table_number: number;
  player1_id: string;
  player1_name: string;
  player2_id: string;
  player2_name: string;
  status: string;
  result: string;
  player1_wins: number;
  player2_wins: number;
  draws: number;
}

const Pairings: React.FC<PairingsProps> = () => {
  const { id } = useParams<{ id: string }>();
  const [tournamentName, setTournamentName] = useState<string>('');
  const [round, setRound] = useState<number>(1);
  const [pairings, setPairings] = useState<Pairing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockTournamentName = 'Friday Night Magic';
    const mockRound = 2;
    
    const mockPairings: Pairing[] = Array.from({ length: 8 }, (_, i) => ({
      match_id: `m${i + 1}`,
      table_number: i + 1,
      player1_id: `p${i * 2 + 1}`,
      player1_name: `Player ${i * 2 + 1}`,
      player2_id: `p${i * 2 + 2}`,
      player2_name: `Player ${i * 2 + 2}`,
      status: i < 5 ? 'completed' : 'in_progress',
      result: i < 5 ? (i % 3 === 0 ? 'win' : i % 3 === 1 ? 'loss' : 'draw') : '',
      player1_wins: i < 5 ? (i % 3 === 0 ? 2 : i % 3 === 1 ? 0 : 1) : 0,
      player2_wins: i < 5 ? (i % 3 === 0 ? 0 : i % 3 === 1 ? 2 : 1) : 0,
      draws: i < 5 ? (i % 3 === 2 ? 1 : 0) : 0
    }));

    setTournamentName(mockTournamentName);
    setRound(mockRound);
    setPairings(mockPairings);
    setLoading(false);
  }, [id]);

  const getMatchResultClass = (result: string) => {
    switch (result) {
      case 'win':
        return 'result-win';
      case 'loss':
        return 'result-loss';
      case 'draw':
        return 'result-draw';
      default:
        return '';
    }
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
        <h1>Round {round} Pairings: {tournamentName}</h1>
        <div>
          <Button variant="outline-primary" className="me-2">
            Print Pairings
          </Button>
          <Link to={`/tournaments/${id}`} className="btn btn-outline-secondary">
            Back to Tournament
          </Link>
        </div>
      </div>

      <Card>
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>Table</th>
                <th>Player 1</th>
                <th>Result</th>
                <th>Player 2</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pairings.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center">No pairings available</td>
                </tr>
              ) : (
                pairings.map((pairing) => (
                  <tr key={pairing.match_id}>
                    <td>{pairing.table_number}</td>
                    <td>
                      <Link to={`/players/${pairing.player1_id}`}>{pairing.player1_name}</Link>
                    </td>
                    <td className={getMatchResultClass(pairing.result)}>
                      {pairing.status === 'completed' ? (
                        `${pairing.player1_wins}-${pairing.player2_wins}${pairing.draws > 0 ? `-${pairing.draws}` : ''}`
                      ) : (
                        'In progress'
                      )}
                    </td>
                    <td>
                      <Link to={`/players/${pairing.player2_id}`}>{pairing.player2_name}</Link>
                    </td>
                    <td>
                      {pairing.status === 'pending' && <Badge bg="secondary">Pending</Badge>}
                      {pairing.status === 'in_progress' && <Badge bg="primary">In Progress</Badge>}
                      {pairing.status === 'completed' && <Badge bg="success">Completed</Badge>}
                    </td>
                    <td>
                      <div className="d-flex gap-2">
                        {pairing.status !== 'completed' ? (
                          <Link to={`/matches/${pairing.match_id}/result`} className="btn btn-sm btn-primary">
                            Enter Result
                          </Link>
                        ) : (
                          <Button variant="sm btn-outline-secondary" disabled>
                            Completed
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      <div className="mt-4">
        <Link to={`/tournaments/${id}/standings`} className="btn btn-primary">
          View Current Standings
        </Link>
      </div>
    </div>
  );
};

// Add missing Alert import
import { Alert } from 'react-bootstrap';

export default Pairings;
