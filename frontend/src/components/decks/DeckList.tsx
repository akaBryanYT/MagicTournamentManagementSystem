import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';

interface DeckListProps {}

interface Deck {
  id: string;
  name: string;
  format: string;
  player_id: string;
  player_name: string;
  tournament_id: string;
  tournament_name: string;
  validation_status: string;
  created_at: string;
}

const DeckList: React.FC<DeckListProps> = () => {
  const navigate = useNavigate();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [formatFilter, setFormatFilter] = useState<string>('all');
  const [filteredDecks, setFilteredDecks] = useState<Deck[]>([]);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockDecks: Deck[] = Array.from({ length: 15 }, (_, i) => ({
      id: `d${i + 1}`,
      name: `Deck ${i + 1}`,
      format: i % 5 === 0 ? 'Standard' : i % 5 === 1 ? 'Modern' : i % 5 === 2 ? 'Commander' : i % 5 === 3 ? 'Draft' : 'Sealed',
      player_id: `p${(i % 8) + 1}`,
      player_name: `Player ${(i % 8) + 1}`,
      tournament_id: `t${(i % 4) + 1}`,
      tournament_name: `Tournament ${(i % 4) + 1}`,
      validation_status: i % 3 === 0 ? 'valid' : i % 3 === 1 ? 'invalid' : 'pending',
      created_at: new Date(Date.now() - i * 86400000).toISOString()
    }));

    setDecks(mockDecks);
    setFilteredDecks(mockDecks);
    setLoading(false);
  }, []);

  useEffect(() => {
    let filtered = decks;
    
    // Apply format filter
    if (formatFilter !== 'all') {
      filtered = filtered.filter(deck => deck.format.toLowerCase() === formatFilter.toLowerCase());
    }
    
    // Apply search term
    if (searchTerm.trim() !== '') {
      filtered = filtered.filter(deck => 
        deck.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deck.player_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        deck.tournament_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredDecks(filtered);
  }, [searchTerm, formatFilter, decks]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleFormatChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormatFilter(e.target.value);
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

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Decks</h1>
        <Link to="/decks/create" className="btn btn-success">
          Register New Deck
        </Link>
      </div>

      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Search Decks</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Search by deck name, player, or tournament"
                  value={searchTerm}
                  onChange={handleSearch}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Filter by Format</Form.Label>
                <Form.Select value={formatFilter} onChange={handleFormatChange}>
                  <option value="all">All Formats</option>
                  <option value="standard">Standard</option>
                  <option value="modern">Modern</option>
                  <option value="commander">Commander</option>
                  <option value="draft">Draft</option>
                  <option value="sealed">Sealed</option>
                </Form.Select>
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
                <th>Deck Name</th>
                <th>Format</th>
                <th>Player</th>
                <th>Tournament</th>
                <th>Validation</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredDecks.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center">No decks found</td>
                </tr>
              ) : (
                filteredDecks.map((deck) => (
                  <tr key={deck.id}>
                    <td>
                      <Link to={`/decks/${deck.id}`}>{deck.name}</Link>
                    </td>
                    <td>{deck.format}</td>
                    <td>
                      <Link to={`/players/${deck.player_id}`}>{deck.player_name}</Link>
                    </td>
                    <td>
                      <Link to={`/tournaments/${deck.tournament_id}`}>{deck.tournament_name}</Link>
                    </td>
                    <td>{getValidationStatusBadge(deck.validation_status)}</td>
                    <td>{new Date(deck.created_at).toLocaleDateString()}</td>
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
    </div>
  );
};

export default DeckList;
