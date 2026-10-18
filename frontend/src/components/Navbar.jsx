import React from 'react';
import { useHealth } from '../hooks/useAgrotech';

export function Navbar({ currentPage, onNavigate }) {
  const health = useHealth();
  const online = health?.status === 'healthy';

  return (
    <nav className="nav">
      <div className="nav-inner">
        <div className="nav-logo">
          <span style={{ fontSize: '1.8rem' }}>🌾</span>
          <div>
            <span>Agro</span><span>Tech</span>
            <div style={{ fontSize: '0.65rem', fontWeight: 400, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
              AI Agriculture Intelligence
            </div>
          </div>
        </div>

        <ul className="nav-links">
          {[
            { id: 'home',    label: 'Home' },
            { id: 'recommend', label: 'Get Recommendations' },
            { id: 'weather', label: 'Weather' },
            { id: 'about',   label: 'About' },
          ].map(({ id, label }) => (
            <li key={id}>
              <a
                href="#"
                className={currentPage === id ? 'active' : ''}
                onClick={e => { e.preventDefault(); onNavigate(id); }}
              >
                {label}
              </a>
            </li>
          ))}
        </ul>

        <div className="nav-status">
          <div className={`status-dot ${online ? '' : 'offline'}`} />
          <span>{online ? `AI Ready · ${health?.crops_available ?? 0} crops` : 'Connecting…'}</span>
        </div>
      </div>
    </nav>
  );
}
