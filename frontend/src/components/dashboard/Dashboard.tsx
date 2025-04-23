import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';
import PlayerService from '../../services/playerService';

interface DashboardProps {}

interface TournamentSummary {
  id: string;
  name: string;
  format: string;
  status: string;
  date: string;
  playerCount: number;
}

interface PlayerSummary {
  id: string;
  name: string;
  tournamentCount: number;
}

const Dashboard: React.FC = () => {
  const [activeTournaments, setActiveTournaments] = useState([]);
  const [recentTournaments, setRecentTournaments] = useState([]);
  const [topPlayers, setTopPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch active tournaments
        const activeResponse = await TournamentService.getActiveTournaments();
        setActiveTournaments(activeResponse || []);
        
        // Fetch recent tournaments
        const recentResponse = await TournamentService.getRecentTournaments();
        setRecentTournaments(recentResponse || []);
        
        // Fetch top players
        const playersResponse = await PlayerService.getAllPlayers();
        setTopPlayers((playersResponse.players || []).slice(0, 5));
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };
  
    fetchData();
  }, []);

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
      <h1 className="mb-4">Tournament Management Dashboard</h1>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>Active Tournaments</Card.Header>
            <Card.Body>
              {activeTournaments.length === 0 ? (
                <p>No active tournaments</p>
              ) : (
                activeTournaments.map(tournament => (
                  <div key={tournament.id} className="mb-3">
                    <h5>
                      <Link to={`/tournaments/${tournament.id}`}>{tournament.name}</Link>
                    </h5>
                    <div className="d-flex justify-content-between">
                      <span>Format: {tournament.format}</span>
                      <span>Players: {tournament.playerCount}</span>
                    </div>
                    <div className="mt-2">
                      <Link to={`/tournaments/${tournament.id}/pairings`} className="btn btn-sm btn-primary me-2">
                        View Pairings
                      </Link>
                      <Link to={`/tournaments/${tournament.id}/standings`} className="btn btn-sm btn-secondary">
                        View Standings
                      </Link>
                    </div>
                  </div>
                ))
              )}
              <div className="mt-3">
                <Link to="/tournaments/create" className="btn btn-success">
                  Create New Tournament
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header>Recent Tournaments</Card.Header>
            <Card.Body>
              {recentTournaments.length === 0 ? (
                <p>No recent tournaments</p>
              ) : (
                recentTournaments.map(tournament => (
                  <div key={tournament.id} className="mb-3">
                    <h5>
                      <Link to={`/tournaments/${tournament.id}`}>{tournament.name}</Link>
                    </h5>
                    <div className="d-flex justify-content-between">
                      <span>Format: {tournament.format}</span>
                      <span>Date: {new Date(tournament.date).toLocaleDateString()}</span>
                    </div>
                    <div className="mt-2">
                      <Link to={`/tournaments/${tournament.id}/standings`} className="btn btn-sm btn-secondary">
                        Final Standings
                      </Link>
                    </div>
                  </div>
                ))
              )}
              <div className="mt-3">
                <Link to="/tournaments" className="btn btn-primary">
                  View All Tournaments
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row>
        <Col md={6}>
          <Card>
            <Card.Header>Top Players</Card.Header>
            <Card.Body>
              {topPlayers.length === 0 ? (
                <p>No player data available</p>
              ) : (
                topPlayers.map(player => (
                  <div key={player.id} className="mb-2">
                    <Link to={`/players/${player.id}`}>{player.name}</Link>
                    <span className="ms-2 text-muted">
                      {player.tournamentCount} tournaments
                    </span>
                  </div>
                ))
              )}
              <div className="mt-3">
                <Link to="/players" className="btn btn-primary">
                  View All Players
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to="/players/create" className="btn btn-primary">
                  Register New Player
                </Link>
                <Link to="/decks/create" className="btn btn-primary">
                  Register New Deck
                </Link>
                <Link to="/tournaments" className="btn btn-primary">
                  Manage Tournaments
                </Link>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
