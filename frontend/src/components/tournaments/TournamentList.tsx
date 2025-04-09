import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Badge, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';

interface TournamentListProps {}

interface Tournament {
  id: string;
  name: string;
  format: string;
  date: string;
  status: string;
  playerCount: number;
  rounds: number;
  currentRound: number;
}

const TournamentList: React.FC<TournamentListProps> = () => {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // In a real implementation, this would be an API call
    // For now, we'll use mock data
    const mockTournaments: Tournament[] = [
      {
        id: '1',
        name: 'Friday Night Magic',
        format: 'Standard',
        date: '2025-03-31',
        status: 'active',
        playerCount: 16,
        rounds: 4,
        currentRound: 2
      },
      {
        id: '2',
        name: 'Commander League',
        format: 'Commander',
        date: '2025-03-30',
        status: 'active',
        playerCount: 12,
        rounds: 3,
        currentRound: 3
      },
      {
        id: '3',
        name: 'Draft Weekend',
        format: 'Draft',
        date: '2025-03-28',
        status: 'completed',
        playerCount: 8,
        rounds: 3,
        currentRound: 3
      },
      {
        id: '4',
        name: 'Modern Showdown',
        format: 'Modern',
        date: '2025-03-25',
        status: 'completed',
        playerCount: 24,
        rounds: 5,
        currentRound: 5
      },
      {
        id: '5',
        name: 'Upcoming Sealed Event',
        format: 'Sealed',
        date: '2025-04-05',
        status: 'planned',
        playerCount: 0,
        rounds: 0,
        currentRound: 0
      }
    ];

    setTournaments(mockTournaments);
    setLoading(false);
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
                    <td>{tournament.playerCount}</td>
                    <td>
                      {tournament.status === 'planned' ? (
                        'Not started'
                      ) : (
                        `${tournament.currentRound} / ${tournament.rounds}`
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
