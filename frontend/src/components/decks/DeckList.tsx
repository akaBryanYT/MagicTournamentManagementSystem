import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import DeckService from '../../services/deckService';

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
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [formatFilter, setFormatFilter] = useState<string>('all');
  const [filteredDecks, setFilteredDecks] = useState<Deck[]>([]);

  useEffect(() => {
    const fetchDecks = async () => {
      try {
        setLoading(true);
        const response = await DeckService.getAllDecks();
        setDecks(response?.decks || []);
        setFilteredDecks(response?.decks || []);
      } catch (err: any) {
        console.error("Error fetching decks:", err);
        setError(err.message || "Failed to load decks");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDecks();
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

  const handleExportDeck = async (deckId: string) => {
    try {
      const result = await DeckService.exportDeckToText(deckId);
      
      // Copy to clipboard
      navigator.clipboard.writeText(result.deck_text)
        .then(() => alert('Deck list copied to clipboard!'))
        .catch(() => alert('Failed to copy deck list to clipboard'));
    } catch (err) {
      console.error('Error exporting deck:', err);
      alert('Failed to export deck');
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

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}

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
                        <Button 
                          variant="outline-secondary" 
                          size="sm"
                          onClick={() => handleExportDeck(deck.id)}
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
    </div>
  );
};

export default DeckList;