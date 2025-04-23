import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Tabs, Tab, Alert, Row, Col, Spinner, Modal, Form } from 'react-bootstrap';
import { Link, useParams, useNavigate } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';
import PlayerService from '../../services/playerService';
import DeckService from '../../services/deckService';
import MatchService from '../../services/matchService';
import BracketView from './BracketView';
import { Player } from '../../types';

interface Tournament {
  id: string;
  name: string;
  format: string;
  structure: string;
  date: string;
  location: string;
  status: string;
  rounds: number;
  current_round: number;
  time_limit?: number;  
  timeLimit?: number;   
  structure_config: {
    allow_intentional_draws: boolean;
    use_seeds_for_byes: boolean;
    seeded: boolean;
    third_place_match: boolean;
    grand_finals_modifier: string;
  };
  format_config: any;
  tiebreakers: {
    match_points: boolean;
    opponents_match_win_percentage: boolean;
    game_win_percentage: boolean;
    opponents_game_win_percentage: boolean;
  };
}

interface Match {
  id: string;
  round: number;
  table_number: number;
  player1_id: string;
  player1_name: string;
  player2_id: string;
  player2_name: string;
  player1_wins: number;
  player2_wins: number;
  draws: number;
  result: string;
  status: string;
  bracket?: string;
  bracket_position?: number;
}

interface Standing {
  id: string;
  rank: number;
  player_id: string;
  player_name: string;
  matches_played: number;
  match_points: number;
  game_points: number;
  match_win_percentage: number;
  game_win_percentage: number;
  opponents_match_win_percentage: number;
  opponents_game_win_percentage: number;
  active: boolean;
}

interface Deck {
  id: string;
  name: string;
  player_id: string;
  player_name: string;
  format: string;
  validation_status: string;
}

const TournamentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [standings, setStandings] = useState<Standing[]>([]);
  const [tournamentDecks, setTournamentDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Modal states
  const [showPlayerRegisterModal, setShowPlayerRegisterModal] = useState<boolean>(false);
  const [showDeckRegistrationModal, setShowDeckRegistrationModal] = useState<boolean>(false);
  const [selectedPlayer, setSelectedPlayer] = useState<string>('');
  const [availablePlayers, setAvailablePlayers] = useState<Player[]>([]);
  const [registering, setRegistering] = useState<boolean>(false);
  
  // Standings edit states
  const [isEditingStandings, setIsEditingStandings] = useState<boolean>(false);
  const [editedStandings, setEditedStandings] = useState<Record<string, Partial<Standing>>>({});
  
  // Deck registration state
  const [deckFormData, setDeckFormData] = useState({
    name: '',
    player_id: '',
    moxfieldUrl: '',
    deckText: ''
  });
  const [deckImportMethod, setDeckImportMethod] = useState<string>('moxfield');

  useEffect(() => {
    if (id) {
      fetchTournamentData();
    }
  }, [id]);

  const fetchTournamentData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch tournament details
      const tournamentData = await TournamentService.getTournamentById(id!);
      setTournament(tournamentData as unknown as Tournament);
      
      // Fetch tournament players
      const playersData = await TournamentService.getTournamentPlayers(id!);
      setPlayers(playersData);
      
      // Fetch current round matches
      if (tournamentData.status === 'active' && tournamentData.current_round > 0) {
        const matchesData = await TournamentService.getRoundPairings(id!, tournamentData.current_round);
        setMatches(matchesData as unknown as Match[]);
      }
      
      // Fetch standings
      const standingsData = await TournamentService.getStandings(id!);
      setStandings(standingsData);
      
      // Fetch decks
      const decksData = await DeckService.getTournamentDecks(id!);
      setTournamentDecks(decksData);
      
      // Fetch available players (for registration)
      fetchAvailablePlayers();
      
    } catch (err: any) {
      console.error('Error fetching tournament data:', err);
      setError(err.message || 'Failed to load tournament data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailablePlayers = async () => {
    try {
      // Fetch all players
      const allPlayersResult = await PlayerService.getAllPlayers();
      const allPlayers = allPlayersResult.players || [];
      
      // Filter out players already in the tournament
      const registeredPlayerIds = new Set(players.map((p: Player) => p.id));
      const available = allPlayers.filter((p: Player) => !registeredPlayerIds.has(p.id));
      
      setAvailablePlayers(available);
    } catch (err) {
      console.error('Error fetching available players:', err);
    }
  };

  const handleStartTournament = async () => {
    try {
      setRefreshing(true);
      const result = await TournamentService.startTournament(id!);
      if (result) {
        fetchTournamentData();
      } else {
        setError('Failed to start tournament');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start tournament');
    } finally {
      setRefreshing(false);
    }
  };

  const handleNextRound = async () => {
    try {
      setRefreshing(true);
      const result = await TournamentService.startNextRound(id!);
      if (result) {
        fetchTournamentData();
      } else {
        setError('Failed to create next round');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create next round');
    } finally {
      setRefreshing(false);
    }
  };

  const handleEndTournament = async () => {
    if (!window.confirm('Are you sure you want to end this tournament? This action cannot be undone.')) {
      return;
    }
    
    try {
      setRefreshing(true);
      const result = await TournamentService.endTournament(id!);
      if (result) {
        fetchTournamentData();
      } else {
        setError('Failed to end tournament');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to end tournament');
    } finally {
      setRefreshing(false);
    }
  };

  const handleRegisterPlayer = async () => {
    if (!selectedPlayer) {
      return;
    }
    
    try {
      setRegistering(true);
      const result = await TournamentService.registerPlayer(id!, selectedPlayer);
      if (result) {
        setShowPlayerRegisterModal(false);
        setSelectedPlayer('');
        fetchTournamentData();
      } else {
        setError('Failed to register player');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to register player');
    } finally {
      setRegistering(false);
    }
  };

  const handleDropPlayer = async (playerId: string) => {
    if (!window.confirm('Are you sure you want to drop this player from the tournament?')) {
      return;
    }
    
    try {
      setRefreshing(true);
      const result = await TournamentService.dropPlayer(id!, playerId);
      if (result) {
        fetchTournamentData();
      } else {
        setError('Failed to drop player');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to drop player');
    } finally {
      setRefreshing(false);
    }
  };
  
  const handleReinstatePlayer = async (playerId: string) => {
    try {
      setRefreshing(true);
      const result = await TournamentService.reinstatePlayer(id!, playerId);
      if (result) {
        fetchTournamentData();
      } else {
        setError('Failed to reinstate player');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to reinstate player');
    } finally {
      setRefreshing(false);
    }
  };

  const toggleEditStandings = () => {
    if (isEditingStandings) {
      // Cancel editing
      setIsEditingStandings(false);
      setEditedStandings({});
    } else {
      // Start editing
      setIsEditingStandings(true);
    }
  };

  const handleStandingChange = (standingId: string, field: string, value: any) => {
    setEditedStandings(prev => ({
      ...prev,
      [standingId]: {
        ...prev[standingId],
        [field]: value
      }
    }));
  };

  const saveStandingsChanges = async () => {
    try {
      setRefreshing(true);
      
      // Prepare updated standings
      const updatedStandings = standings.map(standing => {
        if (editedStandings[standing.id]) {
          return {
            ...standing,
            ...editedStandings[standing.id]
          };
        }
        return standing;
      });
      
      const result = await TournamentService.updateStandings(id!, updatedStandings);
      if (result) {
        setIsEditingStandings(false);
        setEditedStandings({});
        fetchTournamentData();
      } else {
        setError('Failed to update standings');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update standings');
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeckFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setDeckFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleDeckRegistrationSubmit = async () => {
    try {
      setRegistering(true);
      
      if (deckImportMethod === 'moxfield' && deckFormData.moxfieldUrl) {
        // Import from Moxfield
        const result = await DeckService.importDeckFromMoxfield(
          deckFormData.player_id,
          id!,
          deckFormData.moxfieldUrl,
          deckFormData.name
        );
        
        if (result) {
          setShowDeckRegistrationModal(false);
          setDeckFormData({
            name: '',
            player_id: '',
            moxfieldUrl: '',
            deckText: ''
          });
          fetchTournamentData();
        } else {
          setError('Failed to import deck from Moxfield');
        }
      } else if (deckImportMethod === 'text' && deckFormData.deckText) {
        // Import from text
        const result = await DeckService.importDeckFromText(
          deckFormData.player_id,
          id!,
          deckFormData.deckText,
          tournament?.format || 'standard',
          deckFormData.name
        );
        
        if (result) {
          setShowDeckRegistrationModal(false);
          setDeckFormData({
            name: '',
            player_id: '',
            moxfieldUrl: '',
            deckText: ''
          });
          fetchTournamentData();
        } else {
          setError('Failed to import deck from text');
        }
      } else {
        setError('Please provide valid deck information');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to register deck');
    } finally {
      setRegistering(false);
    }
  };
  
  const handlePrintPairings = () => {
    if (!matches || matches.length === 0 || !tournament) return;
    
    const tableContent = matches.map((match) => `
      <tr>
        <td>${match.table_number || '-'}</td>
        <td>${match.player1_name}</td>
        <td>${match.status === 'completed' ? 
            `${match.player1_wins}-${match.player2_wins}${match.draws > 0 ? `-${match.draws}` : ''}` : 
            'In progress'}</td>
        <td>${match.player2_name || 'BYE'}</td>
        <td>${match.status}</td>
      </tr>
    `).join('');
    
    const printWindow = window.open('', '_blank');
    
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Tournament Pairings - ${tournament.name}</title>
            <style>
              body { font-family: Arial, sans-serif; }
              table { border-collapse: collapse; width: 100%; }
              th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
              th { background-color: #f2f2f2; }
            </style>
          </head>
          <body>
            <h1>Round ${tournament.current_round} Pairings: ${tournament.name}</h1>
            <table>
              <thead>
                <tr>
                  <th>Table</th>
                  <th>Player 1</th>
                  <th>Result</th>
                  <th>Player 2</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${tableContent}
              </tbody>
            </table>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
      printWindow.close();
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

  const getRowClassName = (rank: number) => {
    if (rank === 1) return 'first-place';
    if (rank === 2) return 'second-place';
    if (rank === 3) return 'third-place';
    return '';
  };

  const renderPlayerRegisterModal = () => (
    <Modal show={showPlayerRegisterModal} onHide={() => setShowPlayerRegisterModal(false)}>
      <Modal.Header closeButton>
        <Modal.Title>Register Player</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Select Player</Form.Label>
            <Form.Select
              value={selectedPlayer}
              onChange={(e) => setSelectedPlayer(e.target.value)}
            >
              <option value="">-- Select Player --</option>
              {availablePlayers.map(player => (
                <option key={player.id} value={player.id}>{player.name}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setShowPlayerRegisterModal(false)}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleRegisterPlayer} 
          disabled={!selectedPlayer || registering}
        >
          {registering ? (
            <>
              <Spinner as="span" size="sm" animation="border" className="me-2" />
              Registering...
            </>
          ) : (
            'Register Player'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );

  const renderDeckRegistrationModal = () => (
    <Modal 
      show={showDeckRegistrationModal} 
      onHide={() => setShowDeckRegistrationModal(false)}
      size="lg"
    >
      <Modal.Header closeButton>
        <Modal.Title>Register Deck for Tournament</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Player</Form.Label>
            <Form.Select
              name="player_id"
              value={deckFormData.player_id}
              onChange={handleDeckFormChange}
              required
            >
              <option value="">Select Player</option>
              {players.map(player => (
                <option key={player.id} value={player.id}>{player.name}</option>
              ))}
            </Form.Select>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Deck Name</Form.Label>
            <Form.Control
              type="text"
              name="name"
              value={deckFormData.name}
              onChange={handleDeckFormChange}
              required
            />
          </Form.Group>
          
          <Tabs
            activeKey={deckImportMethod}
            onSelect={(k) => k && setDeckImportMethod(k)}
            className="mb-3"
          >
            <Tab eventKey="moxfield" title="Import from Moxfield">
              <Form.Group className="mb-3">
                <Form.Label>Moxfield Deck URL</Form.Label>
                <Form.Control
                  type="text"
                  name="moxfieldUrl"
                  value={deckFormData.moxfieldUrl}
                  onChange={handleDeckFormChange}
                  placeholder="https://www.moxfield.com/decks/your-deck-id"
                />
                <Form.Text className="text-muted">
                  Enter the URL to your Moxfield deck
                </Form.Text>
              </Form.Group>
            </Tab>
            
            <Tab eventKey="text" title="Import from Text">
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
                  value={deckFormData.deckText}
                  onChange={handleDeckFormChange}
                  placeholder="1 Prime Speaker Zegana (FDN) 664
1 Ambuscade (2X2) 133
1 Apothecary Stomper (FDN) 99
// Sideboard
2 Naturalize (M19) 190"
                />
              </Form.Group>
            </Tab>
          </Tabs>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={() => setShowDeckRegistrationModal(false)}>
          Cancel
        </Button>
        <Button 
          variant="primary" 
          onClick={handleDeckRegistrationSubmit}
          disabled={registering || !deckFormData.player_id || !deckFormData.name || 
                   (deckImportMethod === 'moxfield' && !deckFormData.moxfieldUrl) ||
                   (deckImportMethod === 'text' && !deckFormData.deckText)}
        >
          {registering ? (
            <>
              <Spinner as="span" size="sm" animation="border" className="me-2" />
              Registering Deck...
            </>
          ) : (
            'Register Deck'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );

  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading tournament data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger">
        <Alert.Heading>Error</Alert.Heading>
        <p>{error}</p>
        <div className="d-flex justify-content-end">
          <Button variant="outline-danger" onClick={() => navigate('/tournaments')}>
            Back to Tournaments
          </Button>
        </div>
      </Alert>
    );
  }

  if (!tournament) {
    return (
      <Alert variant="warning">
        <Alert.Heading>Tournament Not Found</Alert.Heading>
        <p>The requested tournament could not be found.</p>
        <div className="d-flex justify-content-end">
          <Button variant="outline-warning" onClick={() => navigate('/tournaments')}>
            Back to Tournaments
          </Button>
        </div>
      </Alert>
    );
  }

  return (
    <div>
      {refreshing && (
        <Alert variant="info" className="mb-3">
          <Spinner as="span" size="sm" animation="border" className="me-2" />
          Updating tournament data...
        </Alert>
      )}
      
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>{tournament.name}</h1>
        <div>
          {tournament.status === 'planned' && (
            <Button variant="success" onClick={handleStartTournament} className="me-2" disabled={refreshing}>
              Start Tournament
            </Button>
          )}
          {tournament.status === 'active' && (
            <>
              <Button variant="primary" onClick={handleNextRound} className="me-2" disabled={refreshing}>
                Next Round
              </Button>
              <Button variant="secondary" onClick={handleEndTournament} className="me-2" disabled={refreshing}>
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
                    <th>Game Format</th>
                    <td>{tournament.format}</td>
                  </tr>
                  <tr>
                    <th>Structure</th>
                    <td>{tournament.structure.replace('_', ' ')}</td>
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
                    <td>{players.length}</td>
                  </tr>
                  <tr>
                    <th>Rounds</th>
                    <td>
                      {tournament.status === 'planned' ? (
                        'Not started'
                      ) : (
                        `${tournament.current_round} / ${tournament.rounds}`
                      )}
                    </td>
                  </tr>
                  <tr>
                    <th>Time Limit</th>
                    <td>
                      {tournament.time_limit || tournament.timeLimit ? 
                        `${tournament.time_limit || tournament.timeLimit} minutes` : 
                        'Not specified'}
                    </td>
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
                {tournament.status === 'active' && (
                  <>
                    <Link to={`/tournaments/${id}/pairings`} className="btn btn-primary">
                      View Current Pairings
                    </Link>
                    <Link to={`/tournaments/${id}/standings`} className="btn btn-primary">
                      View Standings
                    </Link>
                  </>
                )}
                
                {tournament.status !== 'completed' && (
                  <>
                    <Button variant="outline-primary" onClick={() => setShowPlayerRegisterModal(true)}>
                      Register Player
                    </Button>
                    <Button variant="outline-primary" onClick={() => setShowDeckRegistrationModal(true)}>
                      Register Deck
                    </Button>
                  </>
                )}
                
                {tournament.status === 'completed' && (
                  <Link to={`/tournaments/${id}/standings`} className="btn btn-secondary">
                    View Final Results
                  </Link>
                )}
                
                <Button 
                  variant="outline-secondary" 
                  onClick={() => window.print()}
                >
                  Print Tournament Info
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
              <div className="d-flex justify-content-between mb-3">
                <h5 className="mb-0">Registered Players ({players.length})</h5>
                {tournament.status !== 'completed' && (
                  <Button 
                    variant="success" 
                    size="sm" 
                    onClick={() => setShowPlayerRegisterModal(true)}
                  >
                    Add Player
                  </Button>
                )}
              </div>
              
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
                            {tournament.status !== 'completed' && (
                              player.active ? (
                                <Button 
                                  variant="warning" 
                                  size="sm"
                                  onClick={() => handleDropPlayer(player.id)}
                                >
                                  Drop
                                </Button>
                              ) : (
                                <Button 
                                  variant="success" 
                                  size="sm"
                                  onClick={() => handleReinstatePlayer(player.id)}
                                >
                                  Reinstate
                                </Button>
                              )
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
                <h5 className="mb-0">
                  {tournament.status === 'active' 
                    ? `Round ${tournament.current_round} Matches` 
                    : tournament.status === 'completed'
                      ? 'Final Round Matches'
                      : 'Matches'}
                </h5>
				{tournament.status === 'active' && (
				<div>
					<Button 
                      variant="outline-primary" 
                      size="sm" 
                      onClick={handlePrintPairings} 
                      className="me-2"
                    >
                      Print Pairings
                    </Button>
					<Link to={`/tournaments/${id}/pairings`} className="btn btn-sm btn-primary">
					Full Pairings View
					</Link>
				</div>
				)}
              </div>

              {tournament.status === 'planned' ? (
                <Alert variant="info">
                  Tournament has not started yet. Start the tournament to generate matches.
                </Alert>
              ) : matches.length === 0 ? (
                <Alert variant="info">
                  No matches available for the current round.
                </Alert>
              ) : (
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
                    {matches.map((match) => (
                      <tr key={match.id}>
                        <td>{match.table_number || '-'}</td>
                        <td>{match.player1_name}</td>
                        <td className={getMatchResultClass(match.result)}>
                          {match.status === 'completed' ? (
                            `${match.player1_wins}-${match.player2_wins}${match.draws > 0 ? `-${match.draws}` : ''}`
                          ) : (
                            match.status === 'in_progress' ? 'In progress' : 'Pending'
                          )}
                        </td>
                        <td>{match.player2_name || 'BYE'}</td>
                        <td>
                          {match.status === 'pending' && <Badge bg="secondary">Pending</Badge>}
                          {match.status === 'in_progress' && <Badge bg="primary">In Progress</Badge>}
                          {match.status === 'completed' && <Badge bg="success">Completed</Badge>}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            {match.status !== 'completed' && match.player2_id ? (
                              <Link to={`/matches/${match.id}/result`} className="btn btn-sm btn-primary">
                                Enter Result
                              </Link>
                            ) : (
                              <Button variant="outline-secondary" size="sm" disabled>
                                {match.player2_id ? 'Completed' : 'BYE'}
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Tab>

        <Tab eventKey="standings" title="Standings">
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">
                  {tournament.status === 'completed' ? 'Final Standings' : 'Current Standings'}
                </h5>
                <div>
                  {tournament.status !== 'completed' && (
                    <Button 
                      variant={isEditingStandings ? "secondary" : "outline-primary"}
                      size="sm" 
                      onClick={toggleEditStandings}
                      className="me-2"
                    >
                      {isEditingStandings ? 'Cancel Editing' : 'Edit Standings'}
                    </Button>
                  )}
                  {isEditingStandings && (
                    <Button 
                      variant="primary" 
                      size="sm" 
                      onClick={saveStandingsChanges}
                      disabled={refreshing}
                    >
                      {refreshing ? (
                        <>
                          <Spinner as="span" size="sm" animation="border" className="me-1" />
                          Saving...
                        </>
                      ) : (
                        'Save Changes'
                      )}
                    </Button>
                  )}
                  {!isEditingStandings && (
                    <Button variant="outline-secondary" size="sm" onClick={() => window.print()}>
                      Print Standings
                    </Button>
                  )}
                </div>
              </div>

              {standings.length === 0 ? (
                <Alert variant="info">
                  No standings available yet. Standings will be generated after matches are played.
                </Alert>
              ) : (
                <Table responsive hover className="standings-table">
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Player</th>
                      <th>Match Points</th>
                      <th>Matches</th>
                      <th>Game Points</th>
                      <th>OMW%</th>
                      <th>GW%</th>
                      <th>OGW%</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {standings.map((standing) => (
                      <tr key={standing.id} className={getRowClassName(standing.rank)}>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="1"
                              size="sm"
                              value={editedStandings[standing.id]?.rank || standing.rank}
                              onChange={(e) => handleStandingChange(standing.id, 'rank', parseInt(e.target.value))}
                            />
                          ) : standing.rank}
                        </td>
                        <td>
                          <Link to={`/players/${standing.player_id}`}>{standing.player_name}</Link>
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              size="sm"
                              value={editedStandings[standing.id]?.match_points || standing.match_points}
                              onChange={(e) => handleStandingChange(standing.id, 'match_points', parseInt(e.target.value))}
                            />
                          ) : standing.match_points}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              size="sm"
                              value={editedStandings[standing.id]?.matches_played || standing.matches_played}
                              onChange={(e) => handleStandingChange(standing.id, 'matches_played', parseInt(e.target.value))}
                            />
                          ) : standing.matches_played}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              size="sm"
                              value={editedStandings[standing.id]?.game_points || standing.game_points}
                              onChange={(e) => handleStandingChange(standing.id, 'game_points', parseInt(e.target.value))}
                            />
                          ) : standing.game_points}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              max="100"
                              step="0.1"
                              size="sm"
                              value={
                                (editedStandings[standing.id]?.opponents_match_win_percentage || 
                                 standing.opponents_match_win_percentage) * 100
                              }
                              onChange={(e) => handleStandingChange(
                                standing.id, 
                                'opponents_match_win_percentage', 
                                parseFloat(e.target.value) / 100
                              )}
                            />
                          ) : (standing.opponents_match_win_percentage * 100).toFixed(1) + '%'}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              max="100"
                              step="0.1"
                              size="sm"
                              value={
                                (editedStandings[standing.id]?.game_win_percentage || 
                                 standing.game_win_percentage) * 100
                              }
                              onChange={(e) => handleStandingChange(
                                standing.id, 
                                'game_win_percentage', 
                                parseFloat(e.target.value) / 100
                              )}
                            />
                          ) : (standing.game_win_percentage * 100).toFixed(1) + '%'}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Control
                              type="number"
                              min="0"
                              max="100"
                              step="0.1"
                              size="sm"
                              value={
                                (editedStandings[standing.id]?.opponents_game_win_percentage || 
                                 standing.opponents_game_win_percentage) * 100
                              }
                              onChange={(e) => handleStandingChange(
                                standing.id, 
                                'opponents_game_win_percentage', 
                                parseFloat(e.target.value) / 100
                              )}
                            />
                          ) : (standing.opponents_game_win_percentage * 100).toFixed(1) + '%'}
                        </td>
                        <td>
                          {isEditingStandings ? (
                            <Form.Select
                              size="sm"
                              value={editedStandings[standing.id]?.active || standing.active ? 'true' : 'false'}
                              onChange={(e) => handleStandingChange(
                                standing.id, 
                                'active', 
                                e.target.value === 'true'
                              )}
                            >
                              <option value="true">Active</option>
                              <option value="false">Dropped</option>
                            </Form.Select>
                          ) : (
                            standing.active ? (
                              <Badge bg="success">Active</Badge>
                            ) : (
                              <Badge bg="danger">Dropped</Badge>
                            )
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}

              <div className="mt-4">
                <h6>Tiebreakers Explanation</h6>
                <ul>
                  <li><strong>Match Points:</strong> 3 points for a win, 1 point for a draw, 0 points for a loss</li>
                  <li><strong>OMW%:</strong> Opponents' Match Win Percentage</li>
                  <li><strong>GW%:</strong> Game Win Percentage</li>
                  <li><strong>OGW%:</strong> Opponents' Game Win Percentage</li>
                </ul>
              </div>
            </Card.Body>
          </Card>
        </Tab>

        {/* Bracket view for single/double elimination tournaments */}
        {tournament.structure === 'single_elimination' && (
          <Tab eventKey="bracket" title="Bracket">
            <Card>
              <Card.Body>
                <h5 className="mb-3">Single Elimination Bracket</h5>
                <BracketView tournamentId={id!} bracketType="single" />
              </Card.Body>
            </Card>
          </Tab>
        )}

        {tournament.structure === 'double_elimination' && (
          <Tab eventKey="bracket" title="Bracket">
            <Card>
              <Card.Body>
                <h5 className="mb-3">Winners Bracket</h5>
                <BracketView tournamentId={id!} bracketType="winners" />
                
                <h5 className="mt-4 mb-3">Losers Bracket</h5>
                <BracketView tournamentId={id!} bracketType="losers" />
              </Card.Body>
            </Card>
          </Tab>
        )}

        <Tab eventKey="decks" title="Decks">
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">Tournament Decks ({tournamentDecks.length})</h5>
                {tournament.status !== 'completed' && (
                  <Button 
                    variant="success" 
                    size="sm" 
                    onClick={() => setShowDeckRegistrationModal(true)}
                  >
                    Register New Deck
                  </Button>
                )}
              </div>

              {tournamentDecks.length === 0 ? (
                <Alert variant="info">
                  No decks have been registered for this tournament yet.
                </Alert>
              ) : (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Player</th>
                      <th>Deck Name</th>
                      <th>Format</th>
                      <th>Validation</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tournamentDecks.map((deck) => (
                      <tr key={deck.id}>
                        <td>
                          <Link to={`/players/${deck.player_id}`}>{deck.player_name}</Link>
                        </td>
                        <td>
                          <Link to={`/decks/${deck.id}`}>{deck.name}</Link>
                        </td>
                        <td>{deck.format}</td>
                        <td>{getValidationStatusBadge(deck.validation_status)}</td>
                        <td>
                          <div className="d-flex gap-2">
                            <Link to={`/decks/${deck.id}`} className="btn btn-sm btn-primary">
                              View
                            </Link>
                            <Button 
                              variant="outline-secondary" 
                              size="sm"
                              onClick={() => {
                                // Export deck to clipboard
                                DeckService.exportDeckToText(deck.id)
                                  .then(result => {
                                    // Copy to clipboard
                                    navigator.clipboard.writeText(result.deck_text)
                                      .then(() => alert('Deck list copied to clipboard!'))
                                      .catch(() => alert('Failed to copy deck list to clipboard'));
                                  })
                                  .catch(err => console.error('Error exporting deck:', err));
                              }}
                            >
                              Export
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
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
                  readOnly
                />
              </Form.Group>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Game Format</Form.Label>
                    <Form.Control
                      type="text"
                      value={tournament.format}
                      disabled
                      readOnly
                    />
                    <Form.Text className="text-muted">
                      Format cannot be changed after tournament creation
                    </Form.Text>
                  </Form.Group>
                </Col>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Tournament Structure</Form.Label>
                    <Form.Control
                      type="text"
                      value={tournament.structure.replace('_', ' ')}
                      disabled
                      readOnly
                    />
                    <Form.Text className="text-muted">
                      Structure cannot be changed after tournament creation
                    </Form.Text>
                  </Form.Group>
                </Col>
              </Row>

              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={tournament.date}
                      disabled={tournament.status !== 'planned'}
                      readOnly
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
                      readOnly
                    />
                  </Form.Group>
                </Col>
              </Row>

              <Form.Group className="mb-3">
                <Form.Label>Round Time Limit (minutes)</Form.Label>
                <Form.Control
                  type="number"
                  value={tournament.time_limit}
                  disabled={tournament.status !== 'planned'}
                  readOnly
                />
              </Form.Group>

              {/* Structure-specific settings */}
              {tournament.structure === 'swiss' && (
                <>
                  <h5 className="mt-4 mb-3">Swiss Settings</h5>
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Allow Intentional Draws"
                      checked={tournament.structure_config.allow_intentional_draws}
                      disabled
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Use Seeds for Byes"
                      checked={tournament.structure_config.use_seeds_for_byes}
                      disabled
                    />
                  </Form.Group>
                </>
              )}

              {tournament.structure === 'single_elimination' && (
                <>
                  <h5 className="mt-4 mb-3">Single Elimination Settings</h5>
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Tournament is Seeded"
                      checked={tournament.structure_config.seeded}
                      disabled
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Include Third Place Match"
                      checked={tournament.structure_config.third_place_match}
                      disabled
                    />
                  </Form.Group>
                </>
              )}

              {tournament.structure === 'double_elimination' && (
                <>
                  <h5 className="mt-4 mb-3">Double Elimination Settings</h5>
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Tournament is Seeded"
                      checked={tournament.structure_config.seeded}
                      disabled
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Grand Finals Format</Form.Label>
                    <Form.Control
                      type="text"
                      value={
                        tournament.structure_config.grand_finals_modifier === 'none' ? 'Standard (Single Match)' :
                        tournament.structure_config.grand_finals_modifier === 'advantage' ? 'Advantage (Winners get 1-0 start)' :
                        'Reset Bracket (Potential Second Match)'
                      }
                      disabled
                      readOnly
                    />
                  </Form.Group>
                </>
              )}

              <h5 className="mt-4 mb-3">Tiebreakers</h5>
              
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Match Points"
                  checked={tournament.tiebreakers.match_points}
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
                  checked={tournament.tiebreakers.opponents_match_win_percentage}
                  disabled
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Game Win Percentage"
                  checked={tournament.tiebreakers.game_win_percentage}
                  disabled
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Opponents' Game Win Percentage"
                  checked={tournament.tiebreakers.opponents_game_win_percentage}
                  disabled
                />
              </Form.Group>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>

      {/* Modals */}
      {renderPlayerRegisterModal()}
      {renderDeckRegistrationModal()}
    </div>
  );
};

export default TournamentDetail;