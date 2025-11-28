import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/api/axios';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Plus, TrendingUp, Clock, CheckCircle2, AlertCircle, Loader2, Globe, Eye } from 'lucide-react';
import { format } from 'date-fns';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAudits();
  }, []);

  const fetchAudits = async () => {
    try {
      const response = await api.get('/audits/');
      setAudits(response.data);
    } catch (error) {
      console.error('Error fetching audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAudit = async (e) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      const response = await api.post('/audits/', { website_url: websiteUrl });
      setAudits([response.data, ...audits]);
      setWebsiteUrl('');
      toast({
        title: "Audit Created!",
        description: "Your SEO audit has been started. It will take a few minutes to complete.",
      });
      setTimeout(() => fetchAudits(), 2000);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to create audit';
      setError(errorMsg);
      toast({
        title: "Failed to Create Audit",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: { bg: 'var(--apollo-warning-light)', color: 'var(--apollo-warning)', icon: Clock, label: 'Pending' },
      crawling: { bg: 'var(--apollo-info-light)', color: 'var(--apollo-info)', icon: Loader2, label: 'Crawling', spin: true },
      analyzing: { bg: 'var(--apollo-info-light)', color: 'var(--apollo-primary)', icon: Loader2, label: 'Analyzing', spin: true },
      generating_report: { bg: 'var(--apollo-info-light)', color: 'var(--apollo-primary)', icon: Loader2, label: 'Generating Report', spin: true },
      completed: { bg: 'var(--apollo-success-light)', color: 'var(--apollo-success)', icon: CheckCircle2, label: 'Completed' },
      failed: { bg: 'var(--apollo-error-light)', color: 'var(--apollo-error)', icon: AlertCircle, label: 'Failed' }
    };

    const variant = variants[status] || variants.pending;
    const Icon = variant.icon;

    return (
      <span className="apollo-badge" style={{ background: variant.bg, color: variant.color, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
        <Icon className={`w-3 h-3 ${variant.spin ? 'animate-spin' : ''}`} />
        {variant.label}
      </span>
    );
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--apollo-success)';
    if (score >= 60) return 'var(--apollo-warning)';
    return 'var(--apollo-error)';
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />

      <div className="apollo-container" style={{ padding: '2rem 1.5rem' }} data-testid="dashboard">
        {/* Page Header */}
        <div style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: 'var(--apollo-gray-900)', marginBottom: '0.5rem' }}>
            SEO Audits
          </h1>
          <p style={{ color: 'var(--apollo-gray-600)', fontSize: '0.875rem' }}>
            Manage and track your website SEO audits
          </p>
        </div>

        {/* Create New Audit Card */}
        <div className="apollo-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--apollo-gray-900)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Plus className="w-5 h-5" style={{ color: 'var(--apollo-primary)' }} />
              Create New SEO Audit
            </h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-600)' }}>
              Enter your website URL to start a comprehensive SEO analysis with 132 checks
            </p>
          </div>

          <form onSubmit={createAudit}>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ flex: '1', minWidth: '300px' }}>
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  required
                  className="apollo-input"
                  data-testid="new-audit-url-input"
                />
              </div>
              <Button 
                type="submit" 
                className="apollo-btn apollo-btn-primary"
                disabled={creating}
                data-testid="create-audit-btn"
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                {creating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Start Audit
                  </>
                )}
              </Button>
            </div>

            {error && (
              <Alert 
                variant="destructive" 
                style={{ 
                  marginTop: '1rem',
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
          </form>
        </div>

        {/* Audits List */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--apollo-gray-900)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <TrendingUp className="w-5 h-5" style={{ color: 'var(--apollo-primary)' }} />
              Your Audits ({audits.length})
            </h2>
          </div>

          {loading ? (
            <div className="apollo-card" style={{ padding: '4rem', textAlign: 'center' }}>
              <Loader2 className="w-12 h-12 animate-spin mx-auto" style={{ color: 'var(--apollo-primary)', marginBottom: '1rem' }} />
              <p style={{ color: 'var(--apollo-gray-600)' }}>Loading your audits...</p>
            </div>
          ) : audits.length === 0 ? (
            <div className="apollo-card" style={{ padding: '4rem', textAlign: 'center' }}>
              <Globe className="w-16 h-16 mx-auto" style={{ color: 'var(--apollo-gray-400)', marginBottom: '1rem' }} />
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--apollo-gray-700)', marginBottom: '0.5rem' }}>
                No audits yet
              </h3>
              <p style={{ color: 'var(--apollo-gray-600)', fontSize: '0.875rem' }}>
                Create your first audit above to get started with SEO analysis
              </p>
            </div>
          ) : (
            <div className="apollo-card">
              <table className="apollo-table">
                <thead>
                  <tr>
                    <th>Website</th>
                    <th>Status</th>
                    <th>Score</th>
                    <th>Pages</th>
                    <th>Checks</th>
                    <th>Created</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((audit) => (
                    <tr key={audit.id} data-testid={`audit-row-${audit.id}`}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <Globe className="w-4 h-4" style={{ color: 'var(--apollo-gray-400)' }} />
                          <span style={{ fontWeight: 500, color: 'var(--apollo-gray-900)' }}>
                            {audit.website_url}
                          </span>
                        </div>
                      </td>
                      <td>{getStatusBadge(audit.status)}</td>
                      <td>
                        {audit.overall_score !== null ? (
                          <span style={{ 
                            fontSize: '1.25rem', 
                            fontWeight: 700, 
                            color: getScoreColor(audit.overall_score) 
                          }}>
                            {audit.overall_score}
                            <span style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-500)', fontWeight: 400 }}>/100</span>
                          </span>
                        ) : (
                          <span style={{ color: 'var(--apollo-gray-400)', fontSize: '0.875rem' }}>-</span>
                        )}
                      </td>
                      <td style={{ color: 'var(--apollo-gray-700)' }}>{audit.pages_crawled || 0}</td>
                      <td>
                        <div style={{ fontSize: '0.875rem' }}>
                          <span style={{ color: 'var(--apollo-success)', fontWeight: 500 }}>{audit.checks_passed}</span>
                          {' / '}
                          <span style={{ color: 'var(--apollo-error)', fontWeight: 500 }}>{audit.checks_failed}</span>
                        </div>
                      </td>
                      <td style={{ color: 'var(--apollo-gray-600)', fontSize: '0.875rem' }}>
                        {format(new Date(audit.created_at), 'MMM dd, yyyy')}
                      </td>
                      <td>
                        <Button
                          size="sm"
                          onClick={() => navigate(`/audit/${audit.id}`)}
                          className="apollo-btn apollo-btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}
                        >
                          <Eye className="w-3 h-3" />
                          View
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <ApolloFooter />
    </div>
  );
};

export default Dashboard;
