import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Tabs, Tab, Alert, Row, Col, Spinner } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';
import PlayerService from '../../services/playerService';
import TournamentService from '../../services/tournamentService';
import DeckService from '../../services/deckService';

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
    const fetchPlayerData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch player details
        const playerData = await PlayerService.getPlayerById(id!);
        setPlayer(playerData);
        
        // Fetch player tournaments
        const tournamentsData = await PlayerService.getPlayerTournaments(id!);
        setTournaments(tournamentsData || []);
        
        // Fetch player decks
        const decksData = await PlayerService.getPlayerDecks(id!);
        setDecks(decksData || []);
        
      } catch (err: any) {
        console.error("Error fetching player data:", err);
        setError(err.message || "Failed to load player data");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchPlayerData();
    }
  }, [id]);

  const handleActivateDeactivate = async () => {
    if (player) {
      try {
        const newStatus = !player.active;
        await PlayerService.togglePlayerStatus(player.id, newStatus);
        
        // Update local state to reflect the change
        setPlayer({
          ...player,
          active: newStatus
        });
      } catch (err) {
        console.error("Error toggling player status:", err);
        setError("Failed to update player status");
      }
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
                    <td>{player.created_at ? new Date(player.created_at).toLocaleDateString() : 'Unknown'}</td>
                  </tr>
                </tbody>
              </Table>
              <div className="mt-3">
                <Button 
                  variant="primary"
                  onClick={() => navigate(`/players/edit/${player.id}`)}
                >
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
                <Link 
                  to={{
                    pathname: "/decks/create",
                    search: `?playerId=${player.id}`
                  }} 
                  className="btn btn-primary"
                >
                  Register New Deck
                </Link>
                <Link 
                  to={{
                    pathname: "/tournaments",
                    search: `?playerId=${player.id}`
                  }} 
                  className="btn btn-primary"
                >
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
                <Link 
                  to={{
                    pathname: "/decks/create",
                    search: `?playerId=${player.id}`
                  }}
                  className="btn btn-sm btn-success"
                >
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
                          <Link to={`/tournaments/${deck.tournament_id}`}>
                            {deck.tournament_name || 'Unknown Tournament'}
                          </Link>
                        </td>
                        <td>{getValidationStatusBadge(deck.validation_status)}</td>
                        <td>
                          <div className="d-flex gap-2">
                            <Link to={`/decks/${deck.id}`} className="btn btn-sm btn-primary">
                              View
                            </Link>
                            <Button 
                              variant="sm btn-outline-secondary"
                              onClick={async () => {
                                try {
                                  const result = await DeckService.exportDeckToText(deck.id);
                                  // Copy to clipboard
                                  navigator.clipboard.writeText(result.deck_text)
                                    .then(() => alert('Deck list copied to clipboard!'))
                                    .catch(() => alert('Failed to copy deck list to clipboard'));
                                } catch (err) {
                                  console.error('Error exporting deck:', err);
                                }
                              }}
                            >
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