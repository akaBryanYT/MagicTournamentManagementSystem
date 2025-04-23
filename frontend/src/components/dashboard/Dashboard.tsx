import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';
import PlayerService from '../../services/playerService';
import { Tournament, Player } from '../../types';

const Dashboard: React.FC = () => {
  const [activeTournaments, setActiveTournaments] = useState<Tournament[]>([]);
  const [recentTournaments, setRecentTournaments] = useState<Tournament[]>([]);
  const [topPlayers, setTopPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch active tournaments
        const activeResponse = await TournamentService.getActiveTournaments();
        setActiveTournaments(activeResponse?.tournaments || []);
        
        // Fetch recent tournaments
        const recentResponse = await TournamentService.getRecentTournaments();
        setRecentTournaments(recentResponse?.tournaments || []);
        
        // Fetch top players
        const playersResponse = await PlayerService.getAllPlayers();
        setTopPlayers(playersResponse?.players || []);
        
      } catch (error: any) {
        console.error("Error fetching dashboard data:", error);
        setError(error.message || "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
  
    fetchData();
  }, []);

  return (
    <div>
      <h1 className="mb-4">Tournament Management Dashboard</h1>
      
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      {loading ? (
        <div className="text-center my-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      ) : (
        <>
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
                          <span>Players: {tournament.playerCount || tournament.player_count || 0}</span>
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
        </>
      )}
    </div>
  );
};

export default Dashboard;