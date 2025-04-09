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
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockPlayers: Player[] = Array.from({ length: 20 }, (_, i) => ({
      id: `p${i + 1}`,
      name: `Player ${i + 1}`,
      email: `player${i + 1}@example.com`,
      phone: `555-${100 + i}`,
      dci_number: i % 3 === 0 ? `12345${i}` : undefined,
      active: i % 7 !== 0,
      tournamentCount: Math.floor(Math.random() * 10)
    }));

    setPlayers(mockPlayers);
    setFilteredPlayers(mockPlayers);
    setLoading(false);
  }, []);

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
