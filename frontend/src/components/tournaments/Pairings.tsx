import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';

// Add missing Alert import
import { Alert } from 'react-bootstrap';

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
    const fetchPairings = async () => {
      try {
        setLoading(true);
        // Fetch tournament details to get name and current round
        const tournamentData = await TournamentService.getTournamentById(id!);
        setTournamentName(tournamentData.name);
        setRound(tournamentData.current_round);
        
        // Fetch pairings for the current round
        const pairingsData = await TournamentService.getRoundPairings(id!, tournamentData.current_round);
        setPairings(pairingsData);
      } catch (err) {
        console.error("Error fetching pairings:", err);
        setError("Failed to load pairings");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchPairings();
    }
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

export default Pairings;
