import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import ApolloNavbar from '@/components/ApolloNavbar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { User, Mail, Lock, Loader2 } from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();
  const { register, user } = useAuth();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await register(formData.email, formData.password, formData.full_name);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />
      
      <div style={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '4rem 1rem',
        minHeight: 'calc(100vh - 80px)'
      }}>
        <div className="apollo-card" style={{ 
          width: '100%',
          maxWidth: '480px',
          padding: '3rem'
        }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <h1 style={{ 
              fontSize: '2rem', 
              fontWeight: 700,
              color: 'var(--apollo-gray-900)',
              marginBottom: '0.5rem'
            }}>
              Create Account
            </h1>
            <p style={{ 
              fontSize: '0.875rem',
              color: 'var(--apollo-gray-600)'
            }}>
              Start your SEO journey today
            </p>
          </div>

          {error && (
            <Alert 
              variant="destructive"
              style={{ 
                marginBottom: '1.5rem',
                background: 'var(--apollo-error-light)',
                border: '1px solid var(--apollo-error)',
                borderRadius: 'var(--apollo-radius)'
              }}
            >
              <AlertDescription style={{ color: 'var(--apollo-error)' }}>
                {error}
              </AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1.5rem' }}>
              <Label 
                htmlFor="full_name"
                style={{ 
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: 'var(--apollo-gray-700)'
                }}
              >
                Full Name
              </Label>
              <div style={{ position: 'relative' }}>
                <User 
                  className="w-5 h-5" 
                  style={{ 
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--apollo-gray-400)'
                  }} 
                />
                <Input
                  id="full_name"
                  name="full_name"
                  type="text"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="register-name-input"
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <Label 
                htmlFor="email"
                style={{ 
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: 'var(--apollo-gray-700)'
                }}
              >
                Email Address
              </Label>
              <div style={{ position: 'relative' }}>
                <Mail 
                  className="w-5 h-5" 
                  style={{ 
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--apollo-gray-400)'
                  }} 
                />
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="register-email-input"
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <Label 
                htmlFor="password"
                style={{ 
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: 'var(--apollo-gray-700)'
                }}
              >
                Password
              </Label>
              <div style={{ position: 'relative' }}>
                <Lock 
                  className="w-5 h-5" 
                  style={{ 
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--apollo-gray-400)'
                  }} 
                />
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="register-password-input"
                />
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <Label 
                htmlFor="confirmPassword"
                style={{ 
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: 'var(--apollo-gray-700)'
                }}
              >
                Confirm Password
              </Label>
              <div style={{ position: 'relative' }}>
                <Lock 
                  className="w-5 h-5" 
                  style={{ 
                    position: 'absolute',
                    left: '0.875rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--apollo-gray-400)'
                  }} 
                />
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="register-confirm-password-input"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="apollo-btn apollo-btn-primary"
              style={{ width: '100%', marginBottom: '1rem' }}
              data-testid="register-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>

            <div style={{ 
              textAlign: 'center',
              fontSize: '0.875rem',
              color: 'var(--apollo-gray-600)'
            }}>
              Already have an account?{' '}
              <Link 
                to="/login" 
                style={{ 
                  color: 'var(--apollo-primary)',
                  textDecoration: 'none',
                  fontWeight: 500
                }}
              >
                Sign in
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
