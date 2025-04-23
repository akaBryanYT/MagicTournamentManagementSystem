import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';

interface TournamentListProps {}

interface Tournament {
  id: string;
  name: string;
  format: string;
  date: string;
  status: string;
  player_count: number;
  current_round: number;
  rounds: number;
}

const TournamentList: React.FC<TournamentListProps> = () => {
  const navigate = useNavigate();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        setLoading(true);
        const response = await TournamentService.getAllTournaments();
        setTournaments(response.tournaments || []);
      } catch (err) {
        console.error("Error fetching tournaments:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTournaments();
  }, []);

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
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Tournaments</h1>
        <Link to="/tournaments/create" className="btn btn-success">
          Create New Tournament
        </Link>
      </div>

      <Card>
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>Name</th>
                <th>Format</th>
                <th>Date</th>
                <th>Status</th>
                <th>Players</th>
                <th>Rounds</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tournaments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center">No tournaments found</td>
                </tr>
              ) : (
                tournaments.map(tournament => (
                  <tr key={tournament.id}>
                    <td>
                      <Link to={`/tournaments/${tournament.id}`}>{tournament.name}</Link>
                    </td>
                    <td>{tournament.format}</td>
                    <td>{new Date(tournament.date).toLocaleDateString()}</td>
                    <td>{getStatusBadge(tournament.status)}</td>
                    <td>{tournament.player_count || 0}</td>
                    <td>
                      {tournament.status === 'planned' ? (
                        'Not started'
                      ) : (
                        `${tournament.current_round} / ${tournament.rounds}`
                      )}
                    </td>
                    <td>
                      <div className="d-flex gap-2">
                        <Link to={`/tournaments/${tournament.id}`} className="btn btn-sm btn-primary">
                          View
                        </Link>
                        {tournament.status === 'active' && (
                          <>
                            <Link to={`/tournaments/${tournament.id}/pairings`} className="btn btn-sm btn-info">
                              Pairings
                            </Link>
                            <Link to={`/tournaments/${tournament.id}/standings`} className="btn btn-sm btn-secondary">
                              Standings
                            </Link>
                          </>
                        )}
                        {tournament.status === 'completed' && (
                          <Link to={`/tournaments/${tournament.id}/standings`} className="btn btn-sm btn-secondary">
                            Results
                          </Link>
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
    </div>
  );
};

export default TournamentList;