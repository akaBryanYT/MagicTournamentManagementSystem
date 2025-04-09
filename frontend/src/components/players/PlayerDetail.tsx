import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Tabs, Tab, Alert, Row, Col, Spinner } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';

interface PlayerDetailProps {}

interface Player {
  id: string;
  name: string;
  email: string;
  phone: string;
  dci_number?: string;
  active: boolean;
  created_at: string;
}

interface Tournament {
  id: string;
  name: string;
  format: string;
  date: string;
  status: string;
}

interface Deck {
  id: string;
  name: string;
  format: string;
  tournament_id: string;
  tournament_name: string;
  validation_status: string;
}

const PlayerDetail: React.FC<PlayerDetailProps> = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [player, setPlayer] = useState<Player | null>(null);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, these would be API calls
    // For now, we'll use mock data
    const mockPlayer: Player = {
      id: id || 'p1',
      name: 'John Doe',
      email: 'john.doe@example.com',
      phone: '555-123-4567',
      dci_number: '12345678',
      active: true,
      created_at: '2025-01-15T12:00:00Z'
    };

    const mockTournaments: Tournament[] = [
      {
        id: 't1',
        name: 'Friday Night Magic',
        format: 'Standard',
        date: '2025-03-31',
        status: 'active'
      },
      {
        id: 't2',
        name: 'Draft Weekend',
        format: 'Draft',
        date: '2025-03-28',
        status: 'completed'
      },
      {
        id: 't3',
        name: 'Modern Showdown',
        format: 'Modern',
        date: '2025-03-25',
        status: 'completed'
      }
    ];

    const mockDecks: Deck[] = [
      {
        id: 'd1',
        name: 'Mono Red Aggro',
        format: 'Standard',
        tournament_id: 't1',
        tournament_name: 'Friday Night Magic',
        validation_status: 'valid'
      },
      {
        id: 'd2',
        name: 'Draft Deck',
        format: 'Draft',
        tournament_id: 't2',
        tournament_name: 'Draft Weekend',
        validation_status: 'valid'
      },
      {
        id: 'd3',
        name: 'Tron',
        format: 'Modern',
        tournament_id: 't3',
        tournament_name: 'Modern Showdown',
        validation_status: 'valid'
      }
    ];

    setPlayer(mockPlayer);
    setTournaments(mockTournaments);
    setDecks(mockDecks);
    setLoading(false);
  }, [id]);

  const handleActivateDeactivate = () => {
    if (player) {
      setPlayer({
        ...player,
        active: !player.active
      });
    }
  };

  const getValidationStatusBadge = (status: string) => {
    switch (status) {
      case 'valid':
        return <Badge bg="success">Valid</Badge>;
      case 'invalid':
        return <Badge bg="danger">Invalid</Badge>;
      case 'pending':
        return <Badge bg="warning">Pending</Badge>;
      default:
        return <Badge bg="secondary">Unknown</Badge>;
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

  if (!player) {
    return (
      <Alert variant="warning">
        Player not found
      </Alert>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{player.name}</h1>
        <div>
          <Button 
            variant={player.active ? "warning" : "success"} 
            onClick={handleActivateDeactivate}
            className="me-2"
          >
            {player.active ? 'Deactivate' : 'Activate'}
          </Button>
          <Link to="/players" className="btn btn-outline-secondary">
            Back to Players
          </Link>
        </div>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>Player Information</Card.Header>
            <Card.Body>
              <Table>
                <tbody>
                  <tr>
                    <th>Email</th>
                    <td>{player.email}</td>
                  </tr>
                  <tr>
                    <th>Phone</th>
                    <td>{player.phone || 'Not provided'}</td>
                  </tr>
                  <tr>
                    <th>DCI Number</th>
                    <td>{player.dci_number || 'Not provided'}</td>
                  </tr>
                  <tr>
                    <th>Status</th>
                    <td>
                      {player.active ? (
                        <Badge bg="success">Active</Badge>
                      ) : (
                        <Badge bg="danger">Inactive</Badge>
                      )}
                    </td>
                  </tr>
                  <tr>
                    <th>Registered Since</th>
                    <td>{new Date(player.created_at).toLocaleDateString()}</td>
                  </tr>
                </tbody>
              </Table>
              <div className="mt-3">
                <Button variant="primary">
                  Edit Player
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to="/decks/create" className="btn btn-primary">
                  Register New Deck
                </Link>
                <Link to="/tournaments" className="btn btn-primary">
                  Register for Tournament
                </Link>
                <Button variant="outline-primary">
                  View Match History
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="tournaments" className="mb-3">
        <Tab eventKey="tournaments" title="Tournaments">
          <Card>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Tournament</th>
                    <th>Format</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tournaments.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="text-center">No tournament history</td>
                    </tr>
                  ) : (
                    tournaments.map((tournament) => (
                      <tr key={tournament.id}>
                        <td>
                          <Link to={`/tournaments/${tournament.id}`}>{tournament.name}</Link>
                        </td>
                        <td>{tournament.format}</td>
                        <td>{new Date(tournament.date).toLocaleDateString()}</td>
                        <td>
                          {tournament.status === 'planned' && <Badge bg="primary">Planned</Badge>}
                          {tournament.status === 'active' && <Badge bg="success">Active</Badge>}
                          {tournament.status === 'completed' && <Badge bg="secondary">Completed</Badge>}
                        </td>
                        <td>
                          <Link to={`/tournaments/${tournament.id}`} className="btn btn-sm btn-primary">
                            View
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="decks" title="Decks">
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Registered Decks</h5>
                <Link to="/decks/create" className="btn btn-sm btn-success">
                  Register New Deck
                </Link>
              </div>

              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Deck Name</th>
                    <th>Format</th>
                    <th>Tournament</th>
                    <th>Validation</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {decks.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="text-center">No decks registered</td>
                    </tr>
                  ) : (
                    decks.map((deck) => (
                      <tr key={deck.id}>
                        <td>
                          <Link to={`/decks/${deck.id}`}>{deck.name}</Link>
                        </td>
                        <td>{deck.format}</td>
                        <td>
                          <Link to={`/tournaments/${deck.tournament_id}`}>{deck.tournament_name}</Link>
                        </td>
                        <td>{getValidationStatusBadge(deck.validation_status)}</td>
                        <td>
                          <div className="d-flex gap-2">
                            <Link to={`/decks/${deck.id}`} className="btn btn-sm btn-primary">
                              View
                            </Link>
                            <Button variant="sm btn-outline-secondary">
                              Export
                            </Button>
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
      </Tabs>
    </div>
  );
};

export default PlayerDetail;
