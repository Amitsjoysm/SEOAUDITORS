import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { BarChart3, Shield, CreditCard, Key, Settings, LogOut } from 'lucide-react';

const ApolloNavbar = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  return (
    <nav className="apollo-navbar">
      <div className="apollo-container apollo-navbar-content">
        <div 
          className="apollo-navbar-logo" 
          style={{ cursor: 'pointer' }}
          onClick={() => navigate(user ? '/dashboard' : '/')}
        >
          <BarChart3 className="w-8 h-8" style={{ color: 'var(--apollo-primary)' }} />
          <span>MJ SEO</span>
        </div>
        
        <div className="apollo-navbar-menu">
          {user ? (
            <>
              <span className="apollo-navbar-link" style={{ cursor: 'default' }}>
                {user.full_name || user.email}
              </span>
              {user.role === 'superadmin' && (
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => navigate('/admin')}
                  className="apollo-navbar-link"
                >
                  <Shield className="w-4 h-4" />
                  Admin
                </Button>
              )}
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/plans')}
                className="apollo-navbar-link"
              >
                <CreditCard className="w-4 h-4" />
                Plans
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/api-tokens')}
                className="apollo-navbar-link"
              >
                <Key className="w-4 h-4" />
                API
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/settings')}
                className="apollo-navbar-link"
              >
                <Settings className="w-4 h-4" />
                Settings
              </Button>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={logout}
                className="apollo-navbar-link"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </>
          ) : (
            <>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => navigate('/login')}
                className="apollo-navbar-link"
              >
                Login
              </Button>
              <Button 
                size="sm"
                onClick={() => navigate('/register')}
                className="apollo-btn apollo-btn-primary"
              >
                Get Started
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default ApolloNavbar;
