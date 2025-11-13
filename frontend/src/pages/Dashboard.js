import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/api/axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { BarChart3, LogOut, Plus, TrendingUp, Clock, CheckCircle2, AlertCircle, Loader2, Settings, Key, Shield, CreditCard } from 'lucide-react';
import { format } from 'date-fns';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
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
      // Poll for updates
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
      pending: { color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30', icon: Clock },
      crawling: { color: 'bg-blue-500/20 text-blue-300 border-blue-500/30', icon: Loader2 },
      analyzing: { color: 'bg-purple-500/20 text-purple-300 border-purple-500/30', icon: Loader2 },
      generating_report: { color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30', icon: Loader2 },
      completed: { color: 'bg-green-500/20 text-green-300 border-green-500/30', icon: CheckCircle2 },
      failed: { color: 'bg-red-500/20 text-red-300 border-red-500/30', icon: AlertCircle }
    };

    const variant = variants[status] || variants.pending;
    const Icon = variant.icon;

    return (
      <Badge className={`${variant.color} border`}>
        <Icon className={`w-3 h-3 mr-1 ${status.includes('ing') ? 'animate-spin' : ''}`} />
        {status.replace('_', ' ')}
      </Badge>
    );
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Navbar */}
      <nav className="border-b border-white/10 backdrop-blur-sm bg-slate-950/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold text-white">MJ SEO</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-300">Hello, {user?.full_name || user?.email}</span>
            {user?.role === 'superadmin' && (
              <Button variant="ghost" className="text-white" onClick={() => navigate('/admin')}>
                <Shield className="w-4 h-4 mr-2" />
                Admin
              </Button>
            )}
            <Button variant="ghost" className="text-white" onClick={() => navigate('/plans')}>
              <CreditCard className="w-4 h-4 mr-2" />
              Plans
            </Button>
            <Button variant="ghost" className="text-white" onClick={() => navigate('/api-tokens')}>
              <Key className="w-4 h-4 mr-2" />
              API
            </Button>
            <Button variant="ghost" className="text-white" onClick={() => navigate('/settings')}>
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="ghost" className="text-white" onClick={logout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8" data-testid="dashboard">
        {/* Create New Audit */}
        <Card className="bg-slate-900/80 border-white/10 backdrop-blur-sm mb-8">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Plus className="w-5 h-5 mr-2 text-blue-400" />
              Create New SEO Audit
            </CardTitle>
            <CardDescription className="text-slate-400">
              Enter your website URL to start a comprehensive SEO analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={createAudit} className="flex gap-4">
              <div className="flex-1">
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  required
                  className="bg-slate-800 border-slate-700 text-white"
                  data-testid="new-audit-url-input"
                />
              </div>
              <Button 
                type="submit" 
                className="bg-blue-600 hover:bg-blue-700" 
                disabled={creating}
                data-testid="create-audit-btn"
              >
                {creating ? (
                  <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</>
                ) : (
                  <><Plus className="mr-2 h-4 w-4" /> Start Audit</>
                )}
              </Button>
            </form>
            {error && (
              <Alert variant="destructive" className="mt-4 bg-red-900/50 border-red-500/50">
                <AlertDescription className="text-red-200">{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Audits List */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2 text-blue-400" />
            Your Audits
          </h2>

          {loading ? (
            <div className="text-center py-12">
              <Loader2 className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
              <p className="text-slate-400">Loading your audits...</p>
            </div>
          ) : audits.length === 0 ? (
            <Card className="bg-slate-900/50 border-white/10 backdrop-blur-sm">
              <CardContent className="py-12 text-center">
                <BarChart3 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 text-lg">No audits yet. Create your first audit above!</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {audits.map((audit) => (
                <Card 
                  key={audit.id} 
                  className="bg-slate-900/50 border-white/10 backdrop-blur-sm hover:bg-slate-900/70 transition-all cursor-pointer"
                  onClick={() => navigate(`/audit/${audit.id}`)}
                  data-testid={`audit-card-${audit.id}`}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold text-white">{audit.website_url}</h3>
                          {getStatusBadge(audit.status)}
                        </div>
                        <p className="text-slate-400 text-sm mb-3">
                          Created {format(new Date(audit.created_at), 'MMM dd, yyyy HH:mm')}
                        </p>
                        <div className="flex gap-6 text-sm">
                          <div>
                            <span className="text-slate-500">Pages: </span>
                            <span className="text-white font-medium">{audit.pages_crawled}</span>
                          </div>
                          <div>
                            <span className="text-slate-500">Checks: </span>
                            <span className="text-white font-medium">{audit.total_checks_run}</span>
                          </div>
                          <div>
                            <span className="text-slate-500">Passed: </span>
                            <span className="text-green-400 font-medium">{audit.checks_passed}</span>
                          </div>
                          <div>
                            <span className="text-slate-500">Failed: </span>
                            <span className="text-red-400 font-medium">{audit.checks_failed}</span>
                          </div>
                        </div>
                      </div>
                      {audit.overall_score !== null && (
                        <div className="text-right">
                          <div className="text-sm text-slate-400 mb-1">Overall Score</div>
                          <div className={`text-4xl font-bold ${getScoreColor(audit.overall_score)}`}>
                            {audit.overall_score}
                          </div>
                          <div className="text-sm text-slate-500">/ 100</div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
