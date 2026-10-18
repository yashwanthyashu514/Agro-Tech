import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { RecommendPage } from './pages/RecommendPage';
import { WeatherPage } from './pages/WeatherPage';
import { AboutPage } from './pages/AboutPage';
import { RaithannaChatWidget } from './components/RaithannaChatWidget';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const navigateTo = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar currentPage={currentPage} onNavigate={navigateTo} />

      <main style={{ flex: 1 }}>
        {currentPage === 'home' && <HomePage onNavigate={navigateTo} />}
        {currentPage === 'recommend' && <RecommendPage />}
        {currentPage === 'weather' && <WeatherPage />}
        {currentPage === 'about' && <AboutPage />}
      </main>

      {/* Raithanna (ರೈತಣ್ಣ) AI Farmer Assistant Chatbot Plugin */}
      <RaithannaChatWidget />

      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '2.5rem 1.5rem',
        background: 'rgba(5, 10, 6, 0.7)',
        marginTop: 'auto'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '1rem',
          fontSize: '0.85rem',
          color: 'var(--text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ fontSize: '1.2rem' }}>🌾</span>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>AgroTech</span>
            <span>· AI Decision Support for Sustainable Agriculture</span>
          </div>
          <div>
            Powered by IMD, ICAR & ISRIC SoilGrids datasets · Production v1.0
          </div>
        </div>
      </footer>
    </div>
  );
}
