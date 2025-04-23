import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Row, Col, Alert, Tabs, Tab, Spinner } from 'react-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import PlayerService from '../../services/playerService';
import TournamentService from '../../services/tournamentService';
import DeckService from '../../services/deckService';
import CardService from '../../services/cardService';

interface Player {
  id: string;
  name: string;
}

interface Tournament {
  id: string;
  name: string;
  format: string;
}

interface CardItem {
  name: string;
  quantity: number;
}

const DeckCreate: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get query params if they exist (for direct navigation from tournament page)
  const queryParams = new URLSearchParams(location.search);
  const preselectedTournamentId = queryParams.get('tournamentId');
  const preselectedPlayerId = queryParams.get('playerId');
  
  const [activeTab, setActiveTab] = useState<string>('moxfield');
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true);
  const [loadingTournaments, setLoadingTournaments] = useState<boolean>(true);
  const [formData, setFormData] = useState({
    name: '',
    format: 'standard',
    player_id: preselectedPlayerId || '',
    tournament_id: preselectedTournamentId || '',
    moxfieldUrl: '',
    deckText: '',
    mainDeck: [] as CardItem[],
    sideboard: [] as CardItem[],
    currentCardSearch: '',
    searchResults: [] as any[],
    selectedCard: null as any,
    cardQuantity: 1
  });
  const [players, setPlayers] = useState<Player[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [validated, setValidated] = useState(false);
  const [cardSearchTimeout, setCardSearchTimeout] = useState<NodeJS.Timeout | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [parsedDeck, setParsedDeck] = useState<{mainDeck: CardItem[], sideboard: CardItem[]} | null>(null);

  // Load players and tournaments
  useEffect(() => {
    fetchPlayers();
    fetchTournaments();
  }, []);

  // Set format based on selected tournament
  useEffect(() => {
    if (formData.tournament_id) {
      const selectedTournament = tournaments.find(t => t.id === formData.tournament_id);
      if (selectedTournament) {
        setFormData(prev => ({
          ...prev,
          format: selectedTournament.format
        }));
      }
    }
  }, [formData.tournament_id, tournaments]);

  const fetchPlayers = async () => {
    try {
      setLoadingPlayers(true);
      const response = await PlayerService.getAllPlayers();
      setPlayers(response.players || []);
    } catch (err) {
      console.error('Error fetching players:', err);
      setError('Failed to load players');
    } finally {
      setLoadingPlayers(false);
    }
  };

  const fetchTournaments = async () => {
    try {
      setLoadingTournaments(true);
      const response = await TournamentService.getAllTournaments();
      // Filter to only show active or planned tournaments
      const activeTournaments = (response.tournaments || []).filter(
        (t: any) => t.status === 'active' || t.status === 'planned'
      );
      setTournaments(activeTournaments as unknown as Tournament[]);
    } catch (err) {
      console.error('Error fetching tournaments:', err);
      setError('Failed to load tournaments');
    } finally {
      setLoadingTournaments(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });

    // Reset parsed deck if changing the text input
    if (name === 'deckText') {
      setParsedDeck(null);
    }

    // Handle card search with debounce
    if (name === 'currentCardSearch') {
      if (cardSearchTimeout) {
        clearTimeout(cardSearchTimeout);
      }
      
      const timeout = setTimeout(() => {
        if (value.trim().length > 2) {
          searchCards(value);
        }
      }, 500);
      
      setCardSearchTimeout(timeout);
    }
  };

  const searchCards = async (query: string) => {
    if (!query || query.length < 3) return;
    
    try {
      const results = await CardService.searchCardsByName(query);
      setFormData(prev => ({
        ...prev,
        searchResults: results || []
      }));
    } catch (err) {
      console.error('Error searching cards:', err);
    }
  };

  const selectCard = (card: any) => {
    setFormData(prev => ({
      ...prev,
      selectedCard: card,
      currentCardSearch: ''
    }));
  };

  const addCardToDeck = (isSideboard: boolean = false) => {
    if (!formData.selectedCard) return;
    
    const newCard = {
      name: formData.selectedCard.name,
      quantity: formData.cardQuantity
    };
    
    setFormData(prev => {
      const target = isSideboard ? 'sideboard' : 'mainDeck';
      const existingCardIndex = prev[target].findIndex(card => card.name === newCard.name);
      
      if (existingCardIndex >= 0) {
        // Update existing card quantity
        const updatedCards = [...prev[target]];
        updatedCards[existingCardIndex].quantity += newCard.quantity;
        return {
          ...prev,
          [target]: updatedCards,
          selectedCard: null,
          cardQuantity: 1
        };
      } else {
        // Add new card
        return {
          ...prev,
          [target]: [...prev[target], newCard],
          selectedCard: null,
          cardQuantity: 1
        };
      }
    });
  };

  const removeCard = (index: number, isSideboard: boolean = false) => {
    const target = isSideboard ? 'sideboard' : 'mainDeck';
    setFormData(prev => ({
      ...prev,
      [target]: prev[target].filter((_, i) => i !== index)
    }));
  };

  const parseDeckText = () => {
    if (!formData.deckText.trim()) {
      setError('Please enter deck list text');
      return;
    }

    try {
      const lines = formData.deckText.split('\n');
      const mainDeck: CardItem[] = [];
      const sideboard: CardItem[] = [];
      
      let inSideboard = false;
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        
        // Skip empty lines
        if (!trimmedLine) continue;
        
        // Check for sideboard marker
        if (trimmedLine.toLowerCase().includes('//') && trimmedLine.toLowerCase().includes('sideboard')) {
          inSideboard = true;
          continue;
        }
        
        // Skip other comment lines
        if (trimmedLine.startsWith('//')) continue;
        
        // Parse card line (e.g., "4 Lightning Bolt" or "1 Prime Speaker Zegana (FDN) 664")
        const match = trimmedLine.match(/^(\d+)\s+([^(]+)(?:\s+\(.*\)\s+.*)?$/);
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
      
      if (mainDeck.length === 0) {
        setError('No valid cards found in the deck list');
        return;
      }

      setParsedDeck({ mainDeck, sideboard });
      setError(null);
      setSuccess('Deck list parsed successfully');

      // Also update the form data
      setFormData(prev => ({
        ...prev,
        mainDeck,
        sideboard
      }));
    } catch (err) {
      console.error('Error parsing deck list:', err);
      setError('Failed to parse deck list. Please check the format.');
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    
    if (form.checkValidity() === false) {
      e.stopPropagation();
      setValidated(true);
      return;
    }
  
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      let deckId;
  
      // Different submission methods based on active tab
      if (activeTab === 'moxfield' && formData.moxfieldUrl) {
        // Submit Moxfield URL
        const result = await DeckService.importDeckFromMoxfield(
          formData.player_id,
          formData.tournament_id,
          formData.moxfieldUrl,
          formData.name
        );
        deckId = result.id;
      } else if ((activeTab === 'import' && parsedDeck) || 
                 (activeTab === 'manual' && formData.mainDeck.length > 0)) {
        // Submit parsed deck or manually added cards
        const deckData = {
          name: formData.name,
          player_id: formData.player_id,
          tournament_id: formData.tournament_id,
          format: formData.format,
          main_deck: activeTab === 'import' ? parsedDeck!.mainDeck : formData.mainDeck,
          sideboard: activeTab === 'import' ? parsedDeck!.sideboard : formData.sideboard
        };
        
        const result = await DeckService.createDeck(deckData);
        deckId = result.id;
      } else {
        throw new Error('No valid deck data provided');
      }
  
      if (deckId) {
        navigate(`/decks/${deckId}`);
      } else {
        throw new Error('Failed to create deck');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create deck');
      window.scrollTo(0, 0);
    } finally {
      setLoading(false);
    }
  };

  const calculateCardCount = (cards: CardItem[]) => {
    return cards.reduce((sum, card) => sum + card.quantity, 0);
  };

  return (
    <div>
      <h1 className="mb-4">Register New Deck</h1>

      <Card>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          {success && <Alert variant="success">{success}</Alert>}

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
                    disabled={!!formData.tournament_id}
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
                  {formData.tournament_id && (
                    <Form.Text className="text-muted">
                      Format is determined by the selected tournament
                    </Form.Text>
                  )}
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
                    disabled={loadingPlayers}
                  >
                    <option value="">Select Player</option>
                    {players.map(player => (
                      <option key={player.id} value={player.id}>{player.name}</option>
                    ))}
                  </Form.Select>
                  {loadingPlayers && (
                    <div className="mt-2">
                      <Spinner size="sm" animation="border" /> Loading players...
                    </div>
                  )}
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
                    disabled={loadingTournaments}
                  >
                    <option value="">Select Tournament</option>
                    {tournaments.map(tournament => (
                      <option key={tournament.id} value={tournament.id}>
                        {tournament.name} ({tournament.format})
                      </option>
                    ))}
                  </Form.Select>
                  {loadingTournaments && (
                    <div className="mt-2">
                      <Spinner size="sm" animation="border" /> Loading tournaments...
                    </div>
                  )}
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
              id="deck-import-tabs"
            >
              <Tab eventKey="moxfield" title="Import from Moxfield">
                <Form.Group className="mb-3">
                  <Form.Label>Moxfield Deck URL</Form.Label>
                  <Form.Control
                    type="text"
                    name="moxfieldUrl"
                    value={formData.moxfieldUrl}
                    onChange={handleChange}
                    placeholder="https://www.moxfield.com/decks/your-deck-id"
                  />
                  <Form.Text className="text-muted">
                    Enter the URL to your Moxfield deck
                  </Form.Text>
                </Form.Group>
              </Tab>
              
              <Tab eventKey="import" title="Import from Text">
                <Form.Group className="mb-3">
                  <Form.Label>Paste Deck List</Form.Label>
                  <Form.Text className="text-muted d-block mb-2">
                    Format: [Quantity] [Card Name] ([Set]) [Collector Number], one card per line.
                    Use "// Sideboard" to mark the beginning of sideboard cards.
                  </Form.Text>
                  <Form.Control
                    as="textarea"
                    rows={10}
                    name="deckText"
                    value={formData.deckText}
                    onChange={handleChange}
                    placeholder="1 Prime Speaker Zegana (FDN) 664
1 Ambuscade (2X2) 133
1 Apothecary Stomper (FDN) 99
// Sideboard
2 Naturalize (M19) 190"
                  />
                </Form.Group>
                <Button 
                  variant="secondary" 
                  type="button" 
                  onClick={parseDeckText}
                  className="mb-3"
                >
                  Parse Deck List
                </Button>

                {parsedDeck && (
                  <div className="mt-3">
                    <h5>Main Deck ({calculateCardCount(parsedDeck.mainDeck)} cards)</h5>
                    <ul className="list-unstyled">
                      {parsedDeck.mainDeck.map((card, index) => (
                        <li key={index}>{card.quantity} {card.name}</li>
                      ))}
                    </ul>
                    
                    {parsedDeck.sideboard.length > 0 && (
                      <>
                        <h5>Sideboard ({calculateCardCount(parsedDeck.sideboard)} cards)</h5>
                        <ul className="list-unstyled">
                          {parsedDeck.sideboard.map((card, index) => (
                            <li key={index}>{card.quantity} {card.name}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                )}
              </Tab>
              
              <Tab eventKey="manual" title="Manual Entry">
                <Row>
                  <Col md={8}>
                    <Form.Group className="mb-3">
                      <Form.Label>Search for Cards</Form.Label>
                      <Form.Control
                        type="text"
                        name="currentCardSearch"
                        value={formData.currentCardSearch}
                        onChange={handleChange}
                        placeholder="Enter card name"
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>Quantity</Form.Label>
                      <Form.Control
                        type="number"
                        name="cardQuantity"
                        value={formData.cardQuantity}
                        onChange={handleChange}
                        min="1"
                        max="99"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                {formData.currentCardSearch.length > 2 && formData.searchResults.length > 0 && (
                  <div className="card-search-results mb-3">
                    <h6>Search Results</h6>
                    <div className="list-group">
                      {formData.searchResults.slice(0, 10).map(card => (
                        <button
                          key={card.id}
                          type="button"
                          className="list-group-item list-group-item-action"
                          onClick={() => selectCard(card)}
                        >
                          {card.name}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {formData.selectedCard && (
                  <div className="selected-card mb-3 p-3 border rounded">
                    <h6>{formData.selectedCard.name}</h6>
                    <div className="d-flex justify-content-end mt-2">
                      <Button 
                        variant="outline-secondary" 
                        size="sm"
                        onClick={() => addCardToDeck(true)}
                        className="me-2"
                      >
                        Add to Sideboard
                      </Button>
                      <Button 
                        variant="primary" 
                        size="sm"
                        onClick={() => addCardToDeck(false)}
                      >
                        Add to Main Deck
                      </Button>
                    </div>
                  </div>
                )}

                <Row>
                  <Col md={6}>
                    <h5>Main Deck ({calculateCardCount(formData.mainDeck)} cards)</h5>
                    <div className="deck-list border rounded p-2 mb-3" style={{minHeight: '200px', maxHeight: '400px', overflowY: 'auto'}}>
                      {formData.mainDeck.length === 0 ? (
                        <p className="text-muted p-2">No cards added</p>
                      ) : (
                        <table className="table table-sm">
                          <tbody>
                            {formData.mainDeck.map((card, index) => (
                              <tr key={index}>
                                <td width="50">{card.quantity}</td>
                                <td>{card.name}</td>
                                <td width="50">
                                  <Button 
                                    variant="outline-danger" 
                                    size="sm"
                                    onClick={() => removeCard(index)}
                                  >
                                    ×
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </Col>
                  <Col md={6}>
                    <h5>Sideboard ({calculateCardCount(formData.sideboard)} cards)</h5>
                    <div className="deck-list border rounded p-2 mb-3" style={{minHeight: '200px', maxHeight: '400px', overflowY: 'auto'}}>
                      {formData.sideboard.length === 0 ? (
                        <p className="text-muted p-2">No cards added</p>
                      ) : (
                        <table className="table table-sm">
                          <tbody>
                            {formData.sideboard.map((card, index) => (
                              <tr key={index}>
                                <td width="50">{card.quantity}</td>
                                <td>{card.name}</td>
                                <td width="50">
                                  <Button 
                                    variant="outline-danger" 
                                    size="sm"
                                    onClick={() => removeCard(index, true)}
                                  >
                                    ×
                                  </Button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </Col>
                </Row>
              </Tab>
            </Tabs>

            <div className="d-flex justify-content-between mt-4">
              <Button variant="secondary" onClick={() => navigate('/decks')}>
                Cancel
              </Button>
              <Button variant="primary" type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Spinner as="span" size="sm" animation="border" className="me-2" />
                    Registering Deck...
                  </>
                ) : (
                  'Register Deck'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default DeckCreate;