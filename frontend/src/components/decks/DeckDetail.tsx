import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Tabs, Tab, Alert, Row, Col, Spinner } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';

interface DeckDetailProps {}

interface Deck {
  id: string;
  name: string;
  format: string;
  player_id: string;
  player_name: string;
  tournament_id: string;
  tournament_name: string;
  validation_status: string;
  validation_errors: string[];
  created_at: string;
  mainDeck: {name: string, quantity: number}[];
  sideboard: {name: string, quantity: number}[];
}

const DeckDetail: React.FC<DeckDetailProps> = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [deck, setDeck] = useState<Deck | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockDeck: Deck = {
      id: id || 'd1',
      name: 'Mono Red Aggro',
      format: 'Standard',
      player_id: 'p1',
      player_name: 'John Doe',
      tournament_id: 't1',
      tournament_name: 'Friday Night Magic',
      validation_status: 'valid',
      validation_errors: [],
      created_at: '2025-03-30T12:00:00Z',
      mainDeck: [
        { name: 'Mountain', quantity: 20 },
        { name: 'Lightning Bolt', quantity: 4 },
        { name: 'Goblin Guide', quantity: 4 },
        { name: 'Monastery Swiftspear', quantity: 4 },
        { name: 'Eidolon of the Great Revel', quantity: 4 },
        { name: 'Skewer the Critics', quantity: 4 },
        { name: 'Light Up the Stage', quantity: 4 },
        { name: 'Lava Spike', quantity: 4 },
        { name: 'Rift Bolt', quantity: 4 },
        { name: 'Searing Blaze', quantity: 4 },
        { name: 'Skullcrack', quantity: 4 }
      ],
      sideboard: [
        { name: 'Smash to Smithereens', quantity: 3 },
        { name: 'Tormod\'s Crypt', quantity: 2 },
        { name: 'Blood Moon', quantity: 2 },
        { name: 'Searing Blood', quantity: 3 },
        { name: 'Exquisite Firecraft', quantity: 3 },
        { name: 'Relic of Progenitus', quantity: 2 }
      ]
    };

    setDeck(mockDeck);
    setLoading(false);
  }, [id]);

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

  const exportDeckToText = () => {
    if (!deck) return '';
    
    let deckText = '// Main Deck\n';
    deck.mainDeck.forEach(card => {
      deckText += `${card.quantity} ${card.name}\n`;
    });
    
    if (deck.sideboard.length > 0) {
      deckText += '\n// Sideboard\n';
      deck.sideboard.forEach(card => {
        deckText += `${card.quantity} ${card.name}\n`;
      });
    }
    
    return deckText;
  };

  const handleExport = () => {
    const deckText = exportDeckToText();
    
    // In a real implementation, this would download a file
    // For now, we'll just log it to the console
    console.log(deckText);
    
    // Create a temporary textarea to copy to clipboard
    const textarea = document.createElement('textarea');
    textarea.value = deckText;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    alert('Deck list copied to clipboard!');
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

  if (!deck) {
    return (
      <Alert variant="warning">
        Deck not found
      </Alert>
    );
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{deck.name}</h1>
        <div>
          <Button variant="primary" onClick={handleExport} className="me-2">
            Export Deck
          </Button>
          <Link to="/decks" className="btn btn-outline-secondary">
            Back to Decks
          </Link>
        </div>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>Deck Information</Card.Header>
            <Card.Body>
              <Table>
                <tbody>
                  <tr>
                    <th>Format</th>
                    <td>{deck.format}</td>
                  </tr>
                  <tr>
                    <th>Player</th>
                    <td>
                      <Link to={`/players/${deck.player_id}`}>{deck.player_name}</Link>
                    </td>
                  </tr>
                  <tr>
                    <th>Tournament</th>
                    <td>
                      <Link to={`/tournaments/${deck.tournament_id}`}>{deck.tournament_name}</Link>
                    </td>
                  </tr>
                  <tr>
                    <th>Validation</th>
                    <td>{getValidationStatusBadge(deck.validation_status)}</td>
                  </tr>
                  <tr>
                    <th>Created</th>
                    <td>{new Date(deck.created_at).toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <th>Main Deck</th>
                    <td>{deck.mainDeck.reduce((sum, card) => sum + card.quantity, 0)} cards</td>
                  </tr>
                  <tr>
                    <th>Sideboard</th>
                    <td>{deck.sideboard.reduce((sum, card) => sum + card.quantity, 0)} cards</td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {deck.validation_status === 'invalid' && deck.validation_errors.length > 0 && (
            <Card className="mb-4 border-danger">
              <Card.Header className="bg-danger text-white">Validation Errors</Card.Header>
              <Card.Body>
                <ul className="mb-0">
                  {deck.validation_errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Button variant="primary" onClick={handleExport}>
                  Export Deck List
                </Button>
                <Button variant="outline-primary">
                  Edit Deck
                </Button>
                <Button variant="outline-primary">
                  Validate Deck
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Tabs defaultActiveKey="mainDeck" className="mb-3">
        <Tab eventKey="mainDeck" title="Main Deck">
          <Card>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Quantity</th>
                    <th>Card Name</th>
                  </tr>
                </thead>
                <tbody>
                  {deck.mainDeck.length === 0 ? (
                    <tr>
                      <td colSpan={2} className="text-center">No cards in main deck</td>
                    </tr>
                  ) : (
                    deck.mainDeck.map((card, index) => (
                      <tr key={index}>
                        <td>{card.quantity}</td>
                        <td>{card.name}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="sideboard" title="Sideboard">
          <Card>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Quantity</th>
                    <th>Card Name</th>
                  </tr>
                </thead>
                <tbody>
                  {deck.sideboard.length === 0 ? (
                    <tr>
                      <td colSpan={2} className="text-center">No cards in sideboard</td>
                    </tr>
                  ) : (
                    deck.sideboard.map((card, index) => (
                      <tr key={index}>
                        <td>{card.quantity}</td>
                        <td>{card.name}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="text" title="Text View">
          <Card>
            <Card.Body>
              <pre className="mb-0">{exportDeckToText()}</pre>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
    </div>
  );
};

export default DeckDetail;
