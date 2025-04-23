import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';

const TournamentCreate: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    name: '',
    format: 'standard',
    structure: 'swiss',
    date: new Date().toISOString().split('T')[0],
    location: '',
    rounds: '',
    timeLimit: '50',
    structureConfig: {
      allowIntentionalDraws: true,
      useSeeds: true,
      seeded: true,
      thirdPlaceMatch: true,
      grandFinalsModifier: 'none',
    },
    formatConfig: {
      podSize: 8,
      packsPerPlayer: 3,
    },
    tiebreakers: {
      matchPoints: true,
      opponentsMatchWinPercentage: true,
      gameWinPercentage: true,
      opponentsGameWinPercentage: true
    }
  });
  const [validated, setValidated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      if (name.startsWith('tiebreakers.')) {
        const tiebreakerName = name.split('.')[1];
        setFormData({
          ...formData,
          tiebreakers: {
            ...formData.tiebreakers,
            [tiebreakerName]: checkbox.checked
          }
        });
      } else if (name.startsWith('structureConfig.')) {
        const configName = name.split('.')[1];
        setFormData({
          ...formData,
          structureConfig: {
            ...formData.structureConfig,
            [configName]: checkbox.checked
          }
        });
      } else if (name.startsWith('formatConfig.')) {
        const configName = name.split('.')[1];
        setFormData({
          ...formData,
          formatConfig: {
            ...formData.formatConfig,
            [configName]: checkbox.checked
          }
        });
      } else {
        setFormData({
          ...formData,
          [name]: checkbox.checked
        });
      }
    } else {
      if (name.startsWith('structureConfig.')) {
        const configName = name.split('.')[1];
        setFormData({
          ...formData,
          structureConfig: {
            ...formData.structureConfig,
            [configName]: value
          }
        });
      } else if (name.startsWith('formatConfig.')) {
        const configName = name.split('.')[1];
        setFormData({
          ...formData,
          formatConfig: {
            ...formData.formatConfig,
            [configName]: type === 'number' ? parseInt(value) : value
          }
        });
      } else {
        setFormData({
          ...formData,
          [name]: value
        });
      }
    }

    // Handle specific format/structure changes
    if (name === 'format') {
      // Set format-specific configuration
      if (value === 'draft') {
        setFormData(prev => ({
          ...prev,
          formatConfig: {
            ...prev.formatConfig,
            podSize: 8,
            packsPerPlayer: 3
          }
        }));
      } else if (value === 'commander') {
        setFormData(prev => ({
          ...prev,
          formatConfig: {
            ...prev.formatConfig,
            podSize: 4,
            pointSystem: 'standard'
          }
        }));
      }
    } else if (name === 'structure') {
      // Set structure-specific configuration
      if (value === 'swiss') {
        setFormData(prev => ({
          ...prev,
          structureConfig: {
            ...prev.structureConfig,
            allowIntentionalDraws: true,
            useSeeds: true
          }
        }));
      } else if (value === 'single_elimination') {
        setFormData(prev => ({
          ...prev,
          structureConfig: {
            ...prev.structureConfig,
            seeded: true,
            thirdPlaceMatch: true
          }
        }));
      } else if (value === 'double_elimination') {
        setFormData(prev => ({
          ...prev,
          structureConfig: {
            ...prev.structureConfig,
            seeded: true,
            grandFinalsModifier: 'none'
          }
        }));
      }
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
    
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
      setValidated(false);
      return;
    }
    
    // Final step - create tournament
    setLoading(true);
    setError(null);
    
    try {
      // Prepare data for API
      const tournamentData = {
        name: formData.name,
        format: formData.format,
        structure: formData.structure,
        date: formData.date,
        location: formData.location,
        rounds: formData.rounds === '' ? 0 : parseInt(formData.rounds),
        time_limit: parseInt(formData.timeLimit),
        status: 'planned',
        current_round: 0,
        structure_config: {
          allow_intentional_draws: formData.structureConfig.allowIntentionalDraws,
          use_seeds_for_byes: formData.structureConfig.useSeeds,
          seeded: formData.structureConfig.seeded,
          third_place_match: formData.structureConfig.thirdPlaceMatch,
          grand_finals_modifier: formData.structureConfig.grandFinalsModifier
        },
        format_config: {
          pod_size: formData.formatConfig.podSize,
          packs_per_player: formData.formatConfig.packsPerPlayer
        },
        tiebreakers: {
          match_points: formData.tiebreakers.matchPoints,
          opponents_match_win_percentage: formData.tiebreakers.opponentsMatchWinPercentage,
          game_win_percentage: formData.tiebreakers.gameWinPercentage,
          opponents_game_win_percentage: formData.tiebreakers.opponentsGameWinPercentage
        }
      };
      
      const formattedData = {
	    ...tournamentData,
	    date: new Date(tournamentData.date).toISOString().split('T')[0]
	  };
	  
	  const result = await TournamentService.createTournament(formattedData);
      
      if (result && result.id) {
        navigate(`/tournaments/${result.id}`);
      } else {
        setError('Failed to create tournament. Please try again.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setCurrentStep(currentStep - 1);
    setValidated(false);
  };

  const renderStep1 = () => (
    <>
      <h4 className="mb-3">Basic Information</h4>
      <Form.Group className="mb-3">
        <Form.Label>Tournament Name</Form.Label>
        <Form.Control
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
        <Form.Control.Feedback type="invalid">
          Please provide a tournament name.
        </Form.Control.Feedback>
      </Form.Group>

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label>Game Format</Form.Label>
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
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label>Tournament Structure</Form.Label>
            <Form.Select
              name="structure"
              value={formData.structure}
              onChange={handleChange}
              required
            >
              <option value="swiss">Swiss</option>
              <option value="single_elimination">Single Elimination</option>
              <option value="double_elimination">Double Elimination</option>
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label>Date</Form.Label>
            <Form.Control
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please select a date.
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group className="mb-3">
            <Form.Label>Location</Form.Label>
            <Form.Control
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              required
            />
            <Form.Control.Feedback type="invalid">
              Please provide a location.
            </Form.Control.Feedback>
          </Form.Group>
        </Col>
      </Row>
    </>
  );

  const renderStep2 = () => (
    <>
      <h4 className="mb-3">Tournament Structure</h4>
      <Form.Group className="mb-3">
        <Form.Label>Number of Rounds (leave blank for automatic)</Form.Label>
        <Form.Control
          type="number"
          name="rounds"
          value={formData.rounds}
          onChange={handleChange}
          min="0"
        />
        <Form.Text className="text-muted">
          If left blank, rounds will be calculated based on player count.
        </Form.Text>
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Label>Round Time Limit (minutes)</Form.Label>
        <Form.Control
          type="number"
          name="timeLimit"
          value={formData.timeLimit}
          onChange={handleChange}
          required
          min="10"
        />
      </Form.Group>

      {/* Structure-specific settings */}
      {formData.structure === 'swiss' && (
        <>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Allow Intentional Draws"
              name="structureConfig.allowIntentionalDraws"
              checked={formData.structureConfig.allowIntentionalDraws}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Use Seeds for Byes (higher seeds get priority for byes)"
              name="structureConfig.useSeeds"
              checked={formData.structureConfig.useSeeds}
              onChange={handleChange}
            />
          </Form.Group>
        </>
      )}

      {formData.structure === 'single_elimination' && (
        <>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Tournament is Seeded (places players in bracket according to seed)"
              name="structureConfig.seeded"
              checked={formData.structureConfig.seeded}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Include Third Place Match"
              name="structureConfig.thirdPlaceMatch"
              checked={formData.structureConfig.thirdPlaceMatch}
              onChange={handleChange}
            />
          </Form.Group>
        </>
      )}

      {formData.structure === 'double_elimination' && (
        <>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Tournament is Seeded"
              name="structureConfig.seeded"
              checked={formData.structureConfig.seeded}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Grand Finals Format</Form.Label>
            <Form.Select
              name="structureConfig.grandFinalsModifier"
              value={formData.structureConfig.grandFinalsModifier}
              onChange={handleChange}
            >
              <option value="none">Standard (Single Match)</option>
              <option value="advantage">Advantage (Winners get 1-0 start)</option>
              <option value="reset">Reset Bracket (Potential Second Match)</option>
            </Form.Select>
          </Form.Group>
        </>
      )}

      {/* Format-specific settings */}
      {formData.format === 'draft' && (
        <>
          <h5 className="mt-4">Draft Format Settings</h5>
          <Form.Group className="mb-3">
            <Form.Label>Pod Size</Form.Label>
            <Form.Control
              type="number"
              name="formatConfig.podSize"
              value={formData.formatConfig.podSize || 8}
              onChange={handleChange}
              min="4"
              max="16"
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Packs per Player</Form.Label>
            <Form.Control
              type="number"
              name="formatConfig.packsPerPlayer"
              value={formData.formatConfig.packsPerPlayer || 3}
              onChange={handleChange}
              min="3"
              max="6"
            />
          </Form.Group>
        </>
      )}

      {formData.format === 'commander' && (
        <>
          <h5 className="mt-4">Commander Format Settings</h5>
          <Form.Group className="mb-3">
            <Form.Label>Pod Size</Form.Label>
            <Form.Control
              type="number"
              name="formatConfig.podSize"
              value={formData.formatConfig.podSize || 4}
              onChange={handleChange}
              min="3"
              max="6"
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Point System</Form.Label>
            <Form.Select
              name="formatConfig.pointSystem"
              value={(formData.formatConfig as any).pointSystem || 'standard'}
              onChange={handleChange}
            >
              <option value="standard">Standard (Win/Loss)</option>
              <option value="achievements">Achievement-Based Points</option>
            </Form.Select>
          </Form.Group>
        </>
      )}
    </>
  );

  const renderStep3 = () => (
    <>
      <h4 className="mb-3">Tiebreakers</h4>
      <p>Select the tiebreakers to use for this tournament (in order of priority):</p>

      <Form.Group className="mb-3">
        <Form.Check
          type="checkbox"
          label="Match Points"
          name="tiebreakers.matchPoints"
          checked={formData.tiebreakers.matchPoints}
          onChange={handleChange}
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
          name="tiebreakers.opponentsMatchWinPercentage"
          checked={formData.tiebreakers.opponentsMatchWinPercentage}
          onChange={handleChange}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Check
          type="checkbox"
          label="Game Win Percentage"
          name="tiebreakers.gameWinPercentage"
          checked={formData.tiebreakers.gameWinPercentage}
          onChange={handleChange}
        />
      </Form.Group>

      <Form.Group className="mb-3">
        <Form.Check
          type="checkbox"
          label="Opponents' Game Win Percentage"
          name="tiebreakers.opponentsGameWinPercentage"
          checked={formData.tiebreakers.opponentsGameWinPercentage}
          onChange={handleChange}
        />
      </Form.Group>

      <Alert variant="info">
        Review your tournament settings before creating. You can make changes later, but some settings cannot be modified once the tournament has started.
      </Alert>
    </>
  );

  return (
    <div>
      <h1 className="mb-4">Create New Tournament</h1>

      <div className="wizard-steps mb-4">
        <Row>
          <Col xs={4}>
            <div className={`wizard-step text-center ${currentStep >= 1 ? 'active' : ''}`}>
              1. Basic Information
            </div>
          </Col>
          <Col xs={4}>
            <div className={`wizard-step text-center ${currentStep >= 2 ? 'active' : ''}`}>
              2. Tournament Structure
            </div>
          </Col>
          <Col xs={4}>
            <div className={`wizard-step text-center ${currentStep >= 3 ? 'active' : ''}`}>
              3. Tiebreakers
            </div>
          </Col>
        </Row>
      </div>

      <Card>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}

          <Form noValidate validated={validated} onSubmit={handleSubmit}>
            {currentStep === 1 && renderStep1()}
            {currentStep === 2 && renderStep2()}
            {currentStep === 3 && renderStep3()}

            <div className="d-flex justify-content-between mt-4">
              {currentStep > 1 ? (
                <Button variant="secondary" onClick={handleBack}>
                  Back
                </Button>
              ) : (
                <div></div>
              )}
              
              <Button 
                variant="primary" 
                type="submit" 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Spinner as="span" size="sm" animation="border" className="me-2" />
                    Creating...
                  </>
                ) : (
                  currentStep < 3 ? 'Next' : 'Create Tournament'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default TournamentCreate;