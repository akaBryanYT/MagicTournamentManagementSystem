import React, { useState, useEffect } from 'react';
import { Card, Spinner, Alert } from 'react-bootstrap';
import { useParams } from 'react-router-dom';
import TournamentService from '../../services/tournamentService';
import { Match } from '../../types';  // Import the Match type

interface BracketViewProps {
  tournamentId: string;
  bracketType: 'single' | 'winners' | 'losers';
}

const BracketView: React.FC<BracketViewProps> = ({ tournamentId, bracketType }) => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBracketData = async () => {
      try {
        setLoading(true);
        const tournament = await TournamentService.getTournamentById(tournamentId);
        
        // Fetch all matches for this tournament
        const allMatches = await TournamentService.getTournamentMatches(tournamentId);
        
        // Filter matches by bracket type
        const bracketMatches = allMatches.filter((match: Match) => match.bracket === bracketType);
        
        // Sort by round and bracket position
        bracketMatches.sort((a: Match, b: Match) => {
          if (a.round !== b.round) return a.round - b.round;
          // Use nullish coalescing to handle undefined values
          return (a.bracket_position ?? 0) - (b.bracket_position ?? 0);
        });
        
        setMatches(bracketMatches);
      } catch (err) {
        setError('Failed to load bracket data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchBracketData();
  }, [tournamentId, bracketType]);

  // Rest of the component remains the same
  if (loading) {
    return <Spinner animation="border" />;
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  // Organize matches by round
  const roundsMap = matches.reduce((acc: any, match) => {
    if (!acc[match.round]) {
      acc[match.round] = [];
    }
    acc[match.round].push(match);
    return acc;
  }, {});

  return (
    <div className="bracket-container">
      {Object.keys(roundsMap).map(round => (
        <div key={round} className="bracket-round">
          <h5>Round {round}</h5>
          <div className="bracket-matches">
            {roundsMap[round].map((match: Match) => (
              <Card key={match.id} className="bracket-match mb-2">
                <Card.Body className="p-2">
                  <div className="d-flex justify-content-between align-items-center mb-1">
                    <span>{match.player1_name || 'TBD'}</span>
                    {match.result === 'win' && <span className="badge bg-success">W</span>}
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <span>{match.player2_name || 'TBD'}</span>
                    {match.result === 'loss' && <span className="badge bg-success">W</span>}
                  </div>
                  {match.status === 'completed' && (
                    <div className="text-center text-muted mt-1">
                      {match.player1_wins}-{match.player2_wins}{match.draws > 0 ? `-${match.draws}` : ''}
                    </div>
                  )}
                </Card.Body>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default BracketView;