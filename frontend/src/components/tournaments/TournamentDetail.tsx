import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Tabs, Tab, Alert, Row, Col, Spinner } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';

interface TournamentDetailProps {}

interface Tournament {
  id: string;
  name: string;
  format: string;
  date: string;
  location: string;
  status: string;
  rounds: number;
  currentRound: number;
  playerCount: number;
  timeLimit: number;
  allowIntentionalDraws: boolean;
  tiebreakers: {
    matchPoints: boolean;
    opponentsMatchWinPercentage: boolean;
    gameWinPercentage: boolean;
    opponentsGameWinPercentage: boolean;
  };
}

interface Player {
  id: string;
  name: string;
  email: string;
  active: boolean;
}

interface Match {
  id: string;
  round: number;
  tableNumber: number;
  player1Id: string;
  player1Name: string;
  player2Id: string;
  player2Name: string;
  player1Wins: number;
  player2Wins: number;
  draws: number;
  result: string;
  status: string;
}

const TournamentDetail: React.FC<TournamentDetailProps> = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, these would be API calls
    // For now, we'll use mock data
    const mockTournament: Tournament = {
      id: id || '1',
      name: 'Friday Night Magic',
      format: 'Standard',
      date: '2025-03-31',
      location: 'Game Store',
      status: 'active',
      rounds: 4,
      currentRound: 2,
      playerCount: 16,
      timeLimit: 50,
      allowIntentionalDraws: true,
      tiebreakers: {
        matchPoints: true,
        opponentsMatchWinPercentage: true,
        gameWinPercentage: true,
        opponentsGameWinPercentage: true
      }
    };

    const mockPlayers: Player[] = Array.from({ length: 16 }, (_, i) => ({
      id: `p${i + 1}`,
      name: `Player ${i + 1}`,
      email: `player${i + 1}@example.com`,
      active: true
    }));

    const mockMatches: Match[] = Array.from({ length: 8 }, (_, i) => ({
      id: `m${i + 1}`,
      round: 2,
      tableNumber: i + 1,
      player1Id: `p${i * 2 + 1}`,
      player1Name: `Player ${i * 2 + 1}`,
      player2Id: `p${i * 2 + 2}`,
      player2Name: `Player ${i * 2 + 2}`,
      player1Wins: i % 3 === 0 ? 2 : i % 3 === 1 ? 0 : 1,
      player2Wins: i % 3 === 0 ? 0 : i % 3 === 1 ? 2 : 1,
      draws: i % 3 === 2 ? 1 : 0,
      result: i % 3 === 0 ? 'win' : i % 3 === 1 ? 'loss' : 'draw',
      status: i < 5 ? 'completed' : 'in_progress'
    }));

    setTournament(mockTournament);
    setPlayers(mockPlayers);
    setMatches(mockMatches);
    setLoading(false);
  }, [id]);

  const handleStartTournament = () => {
    // In a real implementation, this would be an API call
    if (tournament) {
      setTournament({
        ...tournament,
        status: 'active',
        currentRound: 1
      });
    }
  };

  const handleNextRound = () => {
    // In a real implementation, this would be an API call
    if (tournament) {
      setTournament({
        ...tournament,
        currentRound: tournament.currentRound + 1
      });
    }
  };

  const handleEndTournament = () => {
    // In a real implementation, this would be an API call
    if (tournament) {
      setTournament({
        ...tournament,
        status: 'completed'
      });
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'planned':
        return <Badge bg="primary">Planned</Badge>;
      case 'active':
        return <Badge bg="success">Active</Badge>;
      case 'completed':
        return <Badge bg="secondary">Completed</Badge>;
      default:
        return <Badge bg="light">Unknown</Badge>;
    }
  };

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

  if (!tournament) {
    return (
      <Alert variant="warning">
        Tournament not found
      </Alert>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{tournament.name}</h1>
        <div>
          {tournament.status === 'planned' && (
            <Button variant="success" onClick={handleStartTournament} className="me-2">
              Start Tournament
            </Button>
          )}
          {tournament.status === 'active' && (
            <>
              <Button variant="primary" onClick={handleNextRound} className="me-2">
                Next Round
              </Button>
              <Button variant="secondary" onClick={handleEndTournament} className="me-2">
                End Tournament
              </Button>
            </>
          )}
          <Link to="/tournaments" className="btn btn-outline-secondary">
            Back to Tournaments
          </Link>
        </div>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>Tournament Information</Card.Header>
            <Card.Body>
              <Table>
                <tbody>
                  <tr>
                    <th>Format</th>
                    <td>{tournament.format}</td>
                  </tr>
                  <tr>
                    <th>Date</th>
                    <td>{new Date(tournament.date).toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <th>Location</th>
                    <td>{tournament.location}</td>
                  </tr>
                  <tr>
                    <th>Status</th>
                    <td>{getStatusBadge(tournament.status)}</td>
                  </tr>
                  <tr>
                    <th>Players</th>
                    <td>{tournament.playerCount}</td>
                  </tr>
                  <tr>
                    <th>Rounds</th>
                    <td>
                      {tournament.status === 'planned' ? (
                        'Not started'
                      ) : (
                        `${tournament.currentRound} / ${tournament.rounds}`
                      )}
                    </td>
                  </tr>
                  <tr>
                    <th>Time Limit</th>
                    <td>{tournament.timeLimit} minutes</td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to={`/tournaments/${id}/pairings`} className="btn btn-primary">
                  View Current Pairings
                </Link>
                <Link to={`/tournaments/${id}/standings`} className="btn btn-primary">
                  View Standings
                </Link>
                <Button variant="outline-primary">
                  Register Player
                </Button>
                <Button variant="outline-primary">
                  Drop Player
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="players" className="mb-3">
        <Tab eventKey="players" title="Players">
          <Card>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {players.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="text-center">No players registered</td>
                    </tr>
                  ) : (
                    players.map((player, index) => (
                      <tr key={player.id}>
                        <td>{index + 1}</td>
                        <td>
                          <Link to={`/players/${player.id}`}>{player.name}</Link>
                        </td>
                        <td>{player.email}</td>
                        <td>
                          {player.active ? (
                            <Badge bg="success">Active</Badge>
                          ) : (
                            <Badge bg="danger">Dropped</Badge>
                          )}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Link to={`/players/${player.id}`} className="btn btn-sm btn-primary">
                              View
                            </Link>
                            {player.active ? (
                              <Button variant="sm btn-warning">
                                Drop
                              </Button>
                            ) : (
                              <Button variant="sm btn-success">
                                Reinstate
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
        </Tab>

        <Tab eventKey="matches" title="Current Round Matches">
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Round {tournament.currentRound} Matches</h5>
                {tournament.status === 'active' && (
                  <Button variant="outline-primary" size="sm">
                    Print Pairings
                  </Button>
                )}
              </div>

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
                  {matches.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="text-center">No matches in current round</td>
                    </tr>
                  ) : (
                    matches.map((match) => (
                      <tr key={match.id}>
                        <td>{match.tableNumber}</td>
                        <td>{match.player1Name}</td>
                        <td className={getMatchResultClass(match.result)}>
                          {match.status === 'completed' ? (
                            `${match.player1Wins}-${match.player2Wins}${match.draws > 0 ? `-${match.draws}` : ''}`
                          ) : (
                            'In progress'
                          )}
                        </td>
                        <td>{match.player2Name}</td>
                        <td>
                          {match.status === 'pending' && <Badge bg="secondary">Pending</Badge>}
                          {match.status === 'in_progress' && <Badge bg="primary">In Progress</Badge>}
                          {match.status === 'completed' && <Badge bg="success">Completed</Badge>}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            {match.status !== 'completed' ? (
                              <Link to={`/matches/${match.id}/result`} className="btn btn-sm btn-primary">
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
        </Tab>

        <Tab eventKey="settings" title="Settings">
          <Card>
            <Card.Body>
              <h5 className="mb-3">Tournament Settings</h5>
              
              <Form.Group className="mb-3">
                <Form.Label>Tournament Name</Form.Label>
                <Form.Control
                  type="text"
                  value={tournament.name}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Format</Form.Label>
                <Form.Control
                  type="text"
                  value={tournament.format}
                  disabled
                />
                <Form.Text className="text-muted">
                  Format cannot be changed after tournament creation
                </Form.Text>
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={tournament.date}
                      disabled={tournament.status !== 'planned'}
                    />
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Location</Form.Label>
                    <Form.Control
                      type="text"
                      value={tournament.location}
                      disabled={tournament.status !== 'planned'}
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Round Time Limit (minutes)</Form.Label>
                <Form.Control
                  type="number"
                  value={tournament.timeLimit}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Allow Intentional Draws"
                  checked={tournament.allowIntentionalDraws}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              <h5 className="mt-4 mb-3">Tiebreakers</h5>
              
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Match Points"
                  checked={tournament.tiebreakers.matchPoints}
                  disabled
                />
                <Form.Text className="text-muted">
                  Always used as primary tiebreaker
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Opponents' Match Win Percentage"
                  checked={tournament.tiebreakers.opponentsMatchWinPercentage}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Game Win Percentage"
                  checked={tournament.tiebreakers.gameWinPercentage}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Opponents' Game Win Percentage"
                  checked={tournament.tiebreakers.opponentsGameWinPercentage}
                  disabled={tournament.status !== 'planned'}
                />
              </Form.Group>

              {tournament.status === 'planned' && (
                <div className="d-flex justify-content-end mt-4">
                  <Button variant="primary">
                    Save Changes
                  </Button>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
};

// Add missing Form import
import { Form } from 'react-bootstrap';

export default TournamentDetail;
