import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

interface PlayerListProps {}

interface Player {
  id: string;
  name: string;
  email: string;
  phone: string;
  dci_number?: string;
  active: boolean;
  tournamentCount: number;
}

const PlayerList: React.FC<PlayerListProps> = () => {
  const navigate = useNavigate();
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filteredPlayers, setFilteredPlayers] = useState<Player[]>([]);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const response = await PlayerService.getAllPlayers();
        setPlayers(response.players || []);
        setFilteredPlayers(response.players || []);
      } catch (err) {
        console.error("Error fetching players:", err);
      } finally {
        setLoading(false);
      }
    };
  
    fetchPlayers();
  }, []);
  
  // Handle player activation/deactivation
  const handleTogglePlayerStatus = async (playerId: string, currentStatus: boolean) => {
    try {
      await PlayerService.togglePlayerStatus(playerId, !currentStatus);
      
      // Update player list
      setPlayers(prevPlayers => 
        prevPlayers.map(player => 
          player.id === playerId 
            ? {...player, active: !currentStatus} 
            : player
        )
      );
      
      // Update filtered list
      setFilteredPlayers(prevPlayers => 
        prevPlayers.map(player => 
          player.id === playerId 
            ? {...player, active: !currentStatus} 
            : player
        )
      );
    } catch (err) {
      console.error("Error toggling player status:", err);
    }
  };

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredPlayers(players);
    } else {
      const filtered = players.filter(player => 
        player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (player.dci_number && player.dci_number.includes(searchTerm))
      );
      setFilteredPlayers(filtered);
    }
  }, [searchTerm, players]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
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

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Players</h1>
        <Link to="/players/create" className="btn btn-success">
          Register New Player
        </Link>
      </div>

      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Search Players</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Search by name, email, or DCI number"
                  value={searchTerm}
                  onChange={handleSearch}
                />
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card>
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>DCI Number</th>
                <th>Status</th>
                <th>Tournaments</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPlayers.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center">No players found</td>
                </tr>
              ) : (
                filteredPlayers.map((player, index) => (
                  <tr key={player.id}>
                    <td>{index + 1}</td>
                    <td>
                      <Link to={`/players/${player.id}`}>{player.name}</Link>
                    </td>
                    <td>{player.email}</td>
                    <td>{player.phone}</td>
                    <td>{player.dci_number || '-'}</td>
                    <td>
                      {player.active ? (
                        <Badge bg="success">Active</Badge>
                      ) : (
                        <Badge bg="danger">Inactive</Badge>
                      )}
                    </td>
                    <td>{player.tournamentCount}</td>
                    <td>
                      <div className="d-flex gap-2">
                        <Link to={`/players/${player.id}`} className="btn btn-sm btn-primary">
                          View
                        </Link>
                        <Button 
                          variant={player.active ? "warning" : "success"} 
                          size="sm"
                        >
                          {player.active ? 'Deactivate' : 'Activate'}
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
    </div>
  );
};

export default PlayerList;
