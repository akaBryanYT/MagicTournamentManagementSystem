import React, { useState } from 'react';
import { Card, Form, Button, Row, Col, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

interface TournamentCreateProps {}

const TournamentCreate: React.FC<TournamentCreateProps> = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [formData, setFormData] = useState({
    name: '',
    format: 'swiss',
    date: '',
    location: '',
    rounds: '',
    timeLimit: '50',
    allowIntentionalDraws: true,
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
      } else {
        setFormData({
          ...formData,
          [name]: checkbox.checked
        });
      }
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
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
    } else {
      // In a real implementation, this would be an API call
      console.log('Submitting tournament data:', formData);
      
      // Simulate successful creation
      setTimeout(() => {
        navigate('/tournaments');
      }, 1000);
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

      <Form.Group className="mb-3">
        <Form.Label>Format</Form.Label>
        <Form.Select
          name="format"
          value={formData.format}
          onChange={handleChange}
          required
        >
          <option value="swiss">Swiss</option>
          <option value="draft">Draft</option>
          <option value="sealed">Sealed</option>
          <option value="commander">Commander</option>
          <option value="modern">Modern</option>
          <option value="standard">Standard</option>
          <option value="legacy">Legacy</option>
          <option value="vintage">Vintage</option>
        </Form.Select>
      </Form.Group>

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

      {formData.format === 'swiss' && (
        <Form.Group className="mb-3">
          <Form.Check
            type="checkbox"
            label="Allow Intentional Draws"
            name="allowIntentionalDraws"
            checked={formData.allowIntentionalDraws}
            onChange={handleChange}
          />
        </Form.Group>
      )}

      {formData.format === 'draft' && (
        <Alert variant="info">
          Draft pods will be created automatically based on player count.
        </Alert>
      )}

      {formData.format === 'commander' && (
        <Alert variant="info">
          Commander pods will be created with 4 players each.
        </Alert>
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
              
              <Button variant="primary" type="submit">
                {currentStep < 3 ? 'Next' : 'Create Tournament'}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default TournamentCreate;
