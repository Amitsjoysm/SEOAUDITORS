import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import ApolloNavbar from '@/components/ApolloNavbar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Lock, Mail, Loader2, CheckCircle2 } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
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
              Welcome Back
            </h1>
            <p style={{ 
              fontSize: '0.875rem',
              color: 'var(--apollo-gray-600)'
            }}>
              Sign in to your account to continue
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
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="login-email-input"
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
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="apollo-input"
                  style={{ paddingLeft: '2.75rem' }}
                  data-testid="login-password-input"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="apollo-btn apollo-btn-primary"
              style={{ width: '100%', marginBottom: '1rem' }}
              data-testid="login-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            <div style={{ 
              textAlign: 'center',
              fontSize: '0.875rem',
              color: 'var(--apollo-gray-600)'
            }}>
              Don't have an account?{' '}
              <Link 
                to="/register" 
                style={{ 
                  color: 'var(--apollo-primary)',
                  textDecoration: 'none',
                  fontWeight: 500
                }}
              >
                Sign up
              </Link>
            </div>
          </form>

          <div style={{ 
            marginTop: '2rem',
            paddingTop: '2rem',
            borderTop: '1px solid var(--apollo-gray-200)'
          }}>
            <p style={{ 
              fontSize: '0.75rem',
              color: 'var(--apollo-gray-500)',
              textAlign: 'center',
              marginBottom: '1rem'
            }}>
              Demo Credentials
            </p>
            <div style={{ 
              display: 'grid',
              gap: '0.5rem',
              fontSize: '0.75rem'
            }}>
              <div style={{ 
                padding: '0.75rem',
                background: 'var(--apollo-gray-50)',
                borderRadius: 'var(--apollo-radius)',
                border: '1px solid var(--apollo-gray-200)'
              }}>
                <div style={{ fontWeight: 600, color: 'var(--apollo-gray-700)', marginBottom: '0.25rem' }}>
                  Superadmin
                </div>
                <div style={{ color: 'var(--apollo-gray-600)' }}>
                  superadmin@test.com / test123
                </div>
              </div>
              <div style={{ 
                padding: '0.75rem',
                background: 'var(--apollo-gray-50)',
                borderRadius: 'var(--apollo-radius)',
                border: '1px solid var(--apollo-gray-200)'
              }}>
                <div style={{ fontWeight: 600, color: 'var(--apollo-gray-700)', marginBottom: '0.25rem' }}>
                  Test User
                </div>
                <div style={{ color: 'var(--apollo-gray-600)' }}>
                  test@example.com / test123
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
