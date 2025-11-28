import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Mail, MapPin, Phone } from 'lucide-react';

const ApolloFooter = () => {
  const navigate = useNavigate();

  return (
    <footer className="apollo-footer">
      <div className="apollo-container">
        <div className="apollo-footer-grid">
          <div className="apollo-footer-section">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <BarChart3 className="w-8 h-8" style={{ color: 'var(--apollo-primary)' }} />
              <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'white' }}>MJ SEO</span>
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-400)', lineHeight: 1.6 }}>
              AI-powered SEO audit platform with 132 comprehensive checks. 
              Dominate search rankings with actionable insights.
            </p>
          </div>

          <div className="apollo-footer-section">
            <h4>Product</h4>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/'); }} className="apollo-footer-link">Features</a>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/plans'); }} className="apollo-footer-link">Pricing</a>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/dashboard'); }} className="apollo-footer-link">Dashboard</a>
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/api-tokens'); }} className="apollo-footer-link">API Access</a>
          </div>

          <div className="apollo-footer-section">
            <h4>Company</h4>
            <a href="#" className="apollo-footer-link">About Us</a>
            <a href="#" className="apollo-footer-link">Blog</a>
            <a href="#" className="apollo-footer-link">Careers</a>
            <a href="#" className="apollo-footer-link">Contact</a>
          </div>

          <div className="apollo-footer-section">
            <h4>Resources</h4>
            <a href="#" className="apollo-footer-link">Documentation</a>
            <a href="#" className="apollo-footer-link">API Reference</a>
            <a href="#" className="apollo-footer-link">Support Center</a>
            <a href="#" className="apollo-footer-link">Status</a>
          </div>

          <div className="apollo-footer-section">
            <h4>Contact</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Mail className="w-4 h-4" />
              <span style={{ fontSize: '0.875rem' }}>support@mjseo.com</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Phone className="w-4 h-4" />
              <span style={{ fontSize: '0.875rem' }}>+1 (555) 123-4567</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin className="w-4 h-4" />
              <span style={{ fontSize: '0.875rem' }}>San Francisco, CA</span>
            </div>
          </div>
        </div>

        <div className="apollo-footer-bottom">
          <p>&copy; {new Date().getFullYear()} MJ SEO. All rights reserved. Built for SEO excellence.</p>
        </div>
      </div>
    </footer>
  );
};

export default ApolloFooter;
