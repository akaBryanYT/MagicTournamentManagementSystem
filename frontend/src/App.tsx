import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Dashboard from './components/dashboard/Dashboard';
import TournamentList from './components/tournaments/TournamentList';
import TournamentCreate from './components/tournaments/TournamentCreate';
import TournamentDetail from './components/tournaments/TournamentDetail';
import PlayerList from './components/players/PlayerList';
import PlayerCreate from './components/players/PlayerCreate';
import PlayerDetail from './components/players/PlayerDetail';
import DeckList from './components/decks/DeckList';
import DeckCreate from './components/decks/DeckCreate';
import DeckDetail from './components/decks/DeckDetail';
import Pairings from './components/tournaments/Pairings';
import Standings from './components/tournaments/Standings';
import MatchResult from './components/matches/MatchResult';

function App() {
  return (
    <Router>
      <div className="App d-flex flex-column min-vh-100">
        <Header />
        <Container className="flex-grow-1 py-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            
            {/* Tournament Routes */}
            <Route path="/tournaments" element={<TournamentList />} />
            <Route path="/tournaments/create" element={<TournamentCreate />} />
            <Route path="/tournaments/:id" element={<TournamentDetail />} />
            <Route path="/tournaments/:id/pairings" element={<Pairings />} />
            <Route path="/tournaments/:id/standings" element={<Standings />} />
            
            {/* Player Routes */}
            <Route path="/players" element={<PlayerList />} />
            <Route path="/players/create" element={<PlayerCreate />} />
            <Route path="/players/:id" element={<PlayerDetail />} />
            
            {/* Deck Routes */}
            <Route path="/decks" element={<DeckList />} />
            <Route path="/decks/create" element={<DeckCreate />} />
            <Route path="/decks/:id" element={<DeckDetail />} />
            
            {/* Match Routes */}
            <Route path="/matches/:id/result" element={<MatchResult />} />
          </Routes>
        </Container>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
