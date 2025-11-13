import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/api/axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  ArrowLeft, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  TrendingUp,
  Download,
  Loader2,
  Globe,
  Clock,
  MessageCircle,
  FileText
} from 'lucide-react';

const AuditDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingDocx, setDownloadingDocx] = useState(false);

  useEffect(() => {
    fetchAudit();
  }, [id]);

  useEffect(() => {
    if (audit && ['pending', 'crawling', 'analyzing', 'generating_report'].includes(audit.status)) {
      setPolling(true);
      const interval = setInterval(() => {
        fetchAudit();
      }, 3000);
      return () => clearInterval(interval);
    } else {
      setPolling(false);
    }
  }, [audit?.status]);

  const fetchAudit = async () => {
    try {
      const response = await api.get(`/audits/${id}`);
      setAudit(response.data);
    } catch (error) {
      console.error('Error fetching audit:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Technical SEO': Globe,
      'Performance': TrendingUp,
      'On-Page SEO': BarChart3,
      'Content Quality': CheckCircle2
    };
    const Icon = icons[category] || CheckCircle2;
    return <Icon className="w-5 h-5" />;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass': return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case 'fail': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default: return null;
    }
  };

  const groupResultsByCategory = (results) => {
    return results.reduce((acc, result) => {
      if (!acc[result.category]) {
        acc[result.category] = [];
      }
      acc[result.category].push(result);
      return acc;
    }, {});
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await api.get(`/reports/${id}/pdf`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `seo-audit-${audit.website_url.replace(/[^a-z0-9]/gi, '-')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadDocx = async () => {
    setDownloadingDocx(true);
    try {
      const response = await api.get(`/reports/${id}/docx`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `seo-audit-${audit.website_url.replace(/[^a-z0-9]/gi, '-')}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading DOCX:', error);
      alert('Failed to download DOCX report. Please try again.');
    } finally {
      setDownloadingDocx(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-blue-400" />
      </div>
    );
  }

  if (!audit) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Audit not found</div>
      </div>
    );
  }

  const groupedResults = audit.results ? groupResultsByCategory(audit.results) : {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Navbar */}
      <nav className="border-b border-white/10 backdrop-blur-sm bg-slate-950/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Button 
            variant="ghost" 
            className="text-white"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold text-white">MJ SEO</span>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8" data-testid="audit-detail">
        {/* Header Card */}
        <Card className="bg-slate-900/80 border-white/10 backdrop-blur-sm mb-8">
          <CardContent className="p-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-white mb-2">{audit.website_url}</h1>
                <div className="flex items-center gap-4 text-slate-400">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4" />
                    {audit.pages_crawled} pages crawled
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    {audit.total_checks_run} checks completed
                  </div>
                </div>
                {polling && (
                  <div className="mt-4 flex items-center gap-2 text-blue-400">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing audit... Status: {audit.status.replace('_', ' ')}
                  </div>
                )}
              </div>
              {audit.overall_score !== null && (
                <div className="text-center">
                  <div className="text-sm text-slate-400 mb-2">Overall SEO Score</div>
                  <div className={`text-6xl font-bold ${getScoreColor(audit.overall_score)}`}>
                    {audit.overall_score}
                  </div>
                  <div className="text-slate-500 mt-1">/ 100</div>
                  <Progress 
                    value={audit.overall_score} 
                    className="mt-4 w-32"
                  />
                </div>
              )}
            </div>

            {audit.overall_score !== null && (
              <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-white/10">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-400">{audit.checks_passed}</div>
                  <div className="text-slate-400 text-sm">Passed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-red-400">{audit.checks_failed}</div>
                  <div className="text-slate-400 text-sm">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-400">{audit.checks_warning}</div>
                  <div className="text-slate-400 text-sm">Warnings</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results by Category */}
        {audit.results && audit.results.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-4">Detailed Check Results</h2>
            {Object.entries(groupedResults).map(([category, results]) => (
              <Card key={category} className="bg-slate-900/80 border-white/10 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    {getCategoryIcon(category)}
                    {category}
                    <Badge className="ml-auto bg-slate-800 text-white">
                      {results.length} checks
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="space-y-2">
                    {results.map((result, index) => (
                      <AccordionItem key={result.id} value={`item-${index}`} className="border border-white/10 rounded-lg px-4 bg-slate-800/30">
                        <AccordionTrigger className="hover:no-underline">
                          <div className="flex items-center gap-3 flex-1 text-left">
                            {getStatusIcon(result.status)}
                            <span className="text-white font-medium">{result.check_name}</span>
                            {result.impact_score && (
                              <Badge className="ml-auto mr-4 bg-blue-900/50 text-blue-300">
                                Impact: {result.impact_score}/100
                              </Badge>
                            )}
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="text-slate-300 space-y-4 pt-4">
                          {result.current_value && (
                            <div>
                              <div className="text-sm font-semibold text-slate-400 mb-1">Current Value:</div>
                              <div className="text-white">{result.current_value}</div>
                            </div>
                          )}
                          {result.recommended_value && (
                            <div>
                              <div className="text-sm font-semibold text-slate-400 mb-1">Recommended:</div>
                              <div className="text-white">{result.recommended_value}</div>
                            </div>
                          )}
                          {result.pros && result.pros.length > 0 && (
                            <div>
                              <div className="text-sm font-semibold text-green-400 mb-2">✅ Pros:</div>
                              <ul className="list-disc list-inside space-y-1 text-slate-300">
                                {result.pros.map((pro, i) => <li key={i}>{pro}</li>)}
                              </ul>
                            </div>
                          )}
                          {result.cons && result.cons.length > 0 && (
                            <div>
                              <div className="text-sm font-semibold text-red-400 mb-2">❌ Cons:</div>
                              <ul className="list-disc list-inside space-y-1 text-slate-300">
                                {result.cons.map((con, i) => <li key={i}>{con}</li>)}
                              </ul>
                            </div>
                          )}
                          {result.ranking_impact && (
                            <div>
                              <div className="text-sm font-semibold text-yellow-400 mb-1">📊 Ranking Impact:</div>
                              <div className="text-slate-300">{result.ranking_impact}</div>
                            </div>
                          )}
                          {result.solution && (
                            <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                              <div className="text-sm font-semibold text-blue-300 mb-2">💡 Solution:</div>
                              <div className="text-slate-200 whitespace-pre-wrap">{result.solution}</div>
                            </div>
                          )}
                          {result.enhancements && result.enhancements.length > 0 && (
                            <div>
                              <div className="text-sm font-semibold text-purple-400 mb-2">🚀 Enhancement Suggestions:</div>
                              <ul className="list-disc list-inside space-y-1 text-slate-300">
                                {result.enhancements.map((enh, i) => <li key={i}>{enh}</li>)}
                              </ul>
                            </div>
                          )}
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditDetail;
