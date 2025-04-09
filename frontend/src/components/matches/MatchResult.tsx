import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';

// Add missing Alert import
import { Alert } from 'react-bootstrap';

interface MatchResultProps {}

interface Match {
  id: string;
  tournament_id: string;
  tournament_name: string;
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
}

const MatchResult: React.FC<MatchResultProps> = () => {
  const { id } = useParams<{ id: string }>();
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    player1_wins: 0,
    player2_wins: 0,
    draws: 0
  });
  const [validated, setValidated] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockMatch: Match = {
      id: id || 'm1',
      tournament_id: 't1',
      tournament_name: 'Friday Night Magic',
      round: 2,
      table_number: 3,
      player1_id: 'p1',
      player1_name: 'John Doe',
      player2_id: 'p2',
      player2_name: 'Jane Smith',
      player1_wins: 0,
      player2_wins: 0,
      draws: 0,
      result: '',
      status: 'in_progress'
    };

    setMatch(mockMatch);
    setFormData({
      player1_wins: mockMatch.player1_wins,
      player2_wins: mockMatch.player2_wins,
      draws: mockMatch.draws
    });
    setLoading(false);
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: parseInt(value, 10) || 0
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
    
    // Validate that at least one player has wins
    if (formData.player1_wins === 0 && formData.player2_wins === 0 && formData.draws === 0) {
      setError('At least one player must have wins or there must be draws');
      return;
    }
    
    setSubmitting(true);
    setError(null);
    
    // In a real implementation, this would be an API call
    console.log('Submitting match result:', formData);
    
    // Simulate successful submission
    setTimeout(() => {
      setSubmitting(false);
      setSuccess(true);
      
      if (match) {
        setMatch({
          ...match,
          player1_wins: formData.player1_wins,
          player2_wins: formData.player2_wins,
          draws: formData.draws,
          result: formData.player1_wins > formData.player2_wins ? 'win' : 
                 formData.player2_wins > formData.player1_wins ? 'loss' : 'draw',
          status: 'completed'
        });
      }
    }, 1000);
  };

  const handleIntentionalDraw = () => {
    setFormData({
      player1_wins: 0,
      player2_wins: 0,
      draws: 1
    });
    
    setSubmitting(true);
    setError(null);
    
    // In a real implementation, this would be an API call
    console.log('Submitting intentional draw');
    
    // Simulate successful submission
    setTimeout(() => {
      setSubmitting(false);
      setSuccess(true);
      
      if (match) {
        setMatch({
          ...match,
          player1_wins: 0,
          player2_wins: 0,
          draws: 1,
          result: 'draw',
          status: 'completed'
        });
      }
    }, 1000);
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

  if (!match) {
    return (
      <Alert variant="warning">
        Match not found
      </Alert>
    );
  }

  return (
    <div>
      <h1 className="mb-4">Match Result</h1>

      <Card className="mb-4">
        <Card.Header>Match Information</Card.Header>
        <Card.Body>
          <Table>
            <tbody>
              <tr>
                <th>Tournament</th>
                <td>
                  <Link to={`/tournaments/${match.tournament_id}`}>{match.tournament_name}</Link>
                </td>
              </tr>
              <tr>
                <th>Round</th>
                <td>{match.round}</td>
              </tr>
              <tr>
                <th>Table</th>
                <td>{match.table_number}</td>
              </tr>
              <tr>
                <th>Status</th>
                <td>
                  {match.status === 'pending' && <Badge bg="secondary">Pending</Badge>}
                  {match.status === 'in_progress' && <Badge bg="primary">In Progress</Badge>}
                  {match.status === 'completed' && <Badge bg="success">Completed</Badge>}
                </td>
              </tr>
            </tbody>
          </Table>
        </Card.Body>
      </Card>

      {match.status === 'completed' ? (
        <Card>
          <Card.Header>Match Result</Card.Header>
          <Card.Body>
            <div className="text-center">
              <h4>
                <Link to={`/players/${match.player1_id}`}>{match.player1_name}</Link>
                <span className={`mx-2 ${match.result === 'win' ? 'text-success' : match.result === 'loss' ? 'text-danger' : 'text-warning'}`}>
                  {match.player1_wins} - {match.player2_wins}{match.draws > 0 ? ` - ${match.draws}` : ''}
                </span>
                <Link to={`/players/${match.player2_id}`}>{match.player2_name}</Link>
              </h4>
              
              <div className="mt-4">
                <Link to={`/tournaments/${match.tournament_id}/pairings`} className="btn btn-primary">
                  Back to Pairings
                </Link>
              </div>
            </div>
          </Card.Body>
        </Card>
      ) : (
        <Card>
          <Card.Header>Enter Match Result</Card.Header>
          <Card.Body>
            {error && <Alert variant="danger">{error}</Alert>}
            {success && <Alert variant="success">Result submitted successfully!</Alert>}
            
            <Form noValidate validated={validated} onSubmit={handleSubmit}>
              <Row className="align-items-center mb-4">
                <Col xs={5} className="text-end">
                  <h5><Link to={`/players/${match.player1_id}`}>{match.player1_name}</Link></h5>
                </Col>
                <Col xs={2} className="text-center">
                  <h5>vs</h5>
                </Col>
                <Col xs={5}>
                  <h5><Link to={`/players/${match.player2_id}`}>{match.player2_name}</Link></h5>
                </Col>
              </Row>
              
              <Row className="align-items-center mb-4">
                <Col xs={5}>
                  <Form.Group>
                    <Form.Label>{match.player1_name} Wins</Form.Label>
                    <Form.Control
                      type="number"
                      name="player1_wins"
                      value={formData.player1_wins}
                      onChange={handleChange}
                      min="0"
                      max="2"
                      required
                    />
                  </Form.Group>
                </Col>
                <Col xs={2} className="text-center">
                  <Form.Group>
                    <Form.Label>Draws</Form.Label>
                    <Form.Control
                      type="number"
                      name="draws"
                      value={formData.draws}
                      onChange={handleChange}
                      min="0"
                      max="1"
                    />
                  </Form.Group>
                </Col>
                <Col xs={5}>
                  <Form.Group>
                    <Form.Label>{match.player2_name} Wins</Form.Label>
                    <Form.Control
                      type="number"
                      name="player2_wins"
                      value={formData.player2_wins}
                      onChange={handleChange}
                      min="0"
                      max="2"
                      required
                    />
                  </Form.Group>
                </Col>
              </Row>
              
              <div className="d-flex justify-content-between mt-4">
                <Button 
                  variant="secondary" 
                  onClick={handleIntentionalDraw}
                  disabled={submitting || success}
                >
                  Intentional Draw
                </Button>
                <Button 
                  variant="primary" 
                  type="submit"
                  disabled={submitting || success}
                >
                  {submitting ? (
                    <>
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="me-2"
                      />
                      Submitting...
                    </>
                  ) : (
                    'Submit Result'
                  )}
                </Button>
              </div>
            </Form>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default MatchResult;
