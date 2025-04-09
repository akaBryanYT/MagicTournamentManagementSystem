import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Alert, Tabs, Tab } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

interface DeckCreateProps {}

const DeckCreate: React.FC<DeckCreateProps> = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<string>('manual');
  const [formData, setFormData] = useState({
    name: '',
    format: 'standard',
    player_id: '',
    tournament_id: '',
    deckText: '',
    mainDeck: [] as {name: string, quantity: number}[],
    sideboard: [] as {name: string, quantity: number}[]
  });
  const [validated, setValidated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [players, setPlayers] = useState<{id: string, name: string}[]>([
    {id: 'p1', name: 'Player 1'},
    {id: 'p2', name: 'Player 2'},
    {id: 'p3', name: 'Player 3'}
  ]);
  const [tournaments, setTournaments] = useState<{id: string, name: string, format: string}[]>([
    {id: 't1', name: 'Friday Night Magic', format: 'Standard'},
    {id: 't2', name: 'Commander League', format: 'Commander'},
    {id: 't3', name: 'Draft Weekend', format: 'Draft'}
  ]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
    
    // In a real implementation, this would be an API call
    console.log('Submitting deck data:', formData);
    
    // Simulate successful creation
    setTimeout(() => {
      navigate('/decks');
    }, 1000);
  };

  const handleImport = () => {
    if (!formData.deckText.trim()) {
      setError('Please enter deck list text');
      return;
    }

    // Parse deck text
    try {
      const lines = formData.deckText.split('\n');
      const mainDeck: {name: string, quantity: number}[] = [];
      const sideboard: {name: string, quantity: number}[] = [];
      
      let inSideboard = false;
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        
        // Skip empty lines and comments
        if (!trimmedLine || trimmedLine.startsWith('//')) {
          if (trimmedLine.toLowerCase().includes('sideboard')) {
            inSideboard = true;
          }
          continue;
        }
        
        // Parse card line (e.g., "4 Lightning Bolt")
        const match = trimmedLine.match(/^(\d+)\s+(.+)$/);
        if (match) {
          const quantity = parseInt(match[1], 10);
          const cardName = match[2].trim();
          
          const cardEntry = { name: cardName, quantity };
          
          if (inSideboard) {
            sideboard.push(cardEntry);
          } else {
            mainDeck.push(cardEntry);
          }
        }
      }
      
      setFormData({
        ...formData,
        mainDeck,
        sideboard
      });
      
      setError(null);
    } catch (err) {
      setError('Failed to parse deck list. Please check the format.');
    }
  };

  return (
    <div>
      <h1 className="mb-4">Register New Deck</h1>

      <Card>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}

          <Form noValidate validated={validated} onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Deck Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                  />
                  <Form.Control.Feedback type="invalid">
                    Please provide a deck name.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Format</Form.Label>
                  <Form.Select
                    name="format"
                    value={formData.format}
                    onChange={handleChange}
                    required
                  >
                    <option value="standard">Standard</option>
                    <option value="modern">Modern</option>
                    <option value="commander">Commander</option>
                    <option value="legacy">Legacy</option>
                    <option value="vintage">Vintage</option>
                    <option value="draft">Draft</option>
                    <option value="sealed">Sealed</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Player</Form.Label>
                  <Form.Select
                    name="player_id"
                    value={formData.player_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Player</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>{player.name}</option>
                    ))}
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    Please select a player.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tournament</Form.Label>
                  <Form.Select
                    name="tournament_id"
                    value={formData.tournament_id}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Tournament</option>
                    {tournaments.map(tournament => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} ({tournament.format})
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    Please select a tournament.
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Tabs
              activeKey={activeTab}
              onSelect={(k) => k && setActiveTab(k)}
              className="mb-3"
            >
              <Tab eventKey="manual" title="Manual Entry">
                <p>Manual card entry will be implemented in the full version.</p>
              </Tab>
              <Tab eventKey="import" title="Import from Text">
                <Form.Group className="mb-3">
                  <Form.Label>Paste Deck List</Form.Label>
                  <Form.Text className="text-muted d-block mb-2">
                    Format: [Quantity] [Card Name], one card per line. Use "// Sideboard" to mark the beginning of sideboard cards.
                  </Form.Text>
                  <Form.Control
                    as="textarea"
                    rows={10}
                    name="deckText"
                    value={formData.deckText}
                    onChange={handleChange}
                    placeholder="4 Lightning Bolt
3 Goblin Guide
// Sideboard
2 Pyroblast"
                  />
                </Form.Group>
                <Button 
                  variant="secondary" 
                  type="button" 
                  onClick={handleImport}
                  className="mb-3"
                >
                  Parse Deck List
                </Button>

                {formData.mainDeck.length > 0 && (
                  <div className="mt-3">
                    <h5>Main Deck ({formData.mainDeck.reduce((sum, card) => sum + card.quantity, 0)} cards)</h5>
                    <ul className="list-unstyled">
                      {formData.mainDeck.map((card, index) => (
                        <li key={index}>{card.quantity} {card.name}</li>
                      ))}
                    </ul>
                    
                    {formData.sideboard.length > 0 && (
                      <>
                        <h5>Sideboard ({formData.sideboard.reduce((sum, card) => sum + card.quantity, 0)} cards)</h5>
                        <ul className="list-unstyled">
                          {formData.sideboard.map((card, index) => (
                            <li key={index}>{card.quantity} {card.name}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </Tab>
            </Tabs>

            <div className="d-flex justify-content-between mt-4">
              <Button variant="secondary" onClick={() => navigate('/decks')}>
                Cancel
              </Button>
              <Button variant="primary" type="submit">
                Register Deck
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default DeckCreate;
