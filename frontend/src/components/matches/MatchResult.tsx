import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner, Form, Row, Col, Alert } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import MatchService from '../../services/matchService';

interface MatchResultProps {}

interface MatchDetails {
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
  const [match, setMatch] = useState<MatchDetails  | null>(null);
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
    const fetchMatchData = async () => {
      try {
        setLoading(true);
        const matchData = await MatchService.getMatchById(id!);
        setMatch(matchData as unknown as MatchDetails);
        setFormData({
          player1_wins: matchData.player1_wins,
          player2_wins: matchData.player2_wins,
          draws: matchData.draws
        });
      } catch (err) {
        console.error("Error fetching match data:", err);
        setError("Failed to load match data");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchMatchData();
    }
  }, [id]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: parseInt(value, 10) || 0
    });
  };
  
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
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
    
    try {
      const result = await MatchService.submitResult(id!, formData);
      
      if (result) {
        setSuccess(true);
        // Refresh match data
        const updatedMatch = await MatchService.getMatchById(id!);
        setMatch(updatedMatch as unknown as MatchDetails);
      } else {
        setError('Failed to submit match result');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting the result');
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleIntentionalDraw = async () => {
    setSubmitting(true);
    setError(null);
    
    try {
      const result = await MatchService.submitIntentionalDraw(id!);
      
      if (result) {
        setSuccess(true);
        // Refresh match data
        const updatedMatch = await MatchService.getMatchById(id!);
        setMatch(updatedMatch as unknown as MatchDetails);
      } else {
        setError('Failed to submit intentional draw');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while submitting the draw');
    } finally {
      setSubmitting(false);
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