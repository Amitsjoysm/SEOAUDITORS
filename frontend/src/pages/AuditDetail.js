import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/api/axios';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/hooks/use-toast';
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
  const { toast } = useToast();
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
    if (score >= 80) return 'var(--apollo-success)';
    if (score >= 60) return 'var(--apollo-warning)';
    return 'var(--apollo-error)';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'Technical SEO': Globe,
      'Performance': TrendingUp,
      'On-Page SEO': BarChart3,
      'Content Quality': CheckCircle2
    };
    const Icon = icons[category] || CheckCircle2;
    return <Icon className="w-5 h-5" style={{ color: 'var(--apollo-primary)' }} />;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass': return <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)' }} />;
      case 'fail': return <XCircle className="w-5 h-5" style={{ color: 'var(--apollo-error)' }} />;
      case 'warning': return <AlertTriangle className="w-5 h-5" style={{ color: 'var(--apollo-warning)' }} />;
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
      
      // Check if response is actually a blob or an error
      if (response.data.type && response.data.type.includes('application/json')) {
        // Response is JSON error, not a PDF blob
        const text = await response.data.text();
        const errorData = JSON.parse(text);
        throw new Error(errorData.detail || 'Failed to generate PDF');
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      const safeFilename = `seo-audit-${(audit?.website_url || 'report').replace(/[^a-z0-9]/gi, '-')}.pdf`;
      link.setAttribute('download', safeFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast({
        title: "Success!",
        description: "PDF report downloaded successfully.",
      });
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast({
        title: "Download Failed",
        description: error.message || error.response?.data?.detail || "Failed to download PDF report. Please try again.",
        variant: "destructive",
      });
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
      
      // Check if response is actually a blob or an error
      if (response.data.type && response.data.type.includes('application/json')) {
        // Response is JSON error, not a DOCX blob
        const text = await response.data.text();
        const errorData = JSON.parse(text);
        throw new Error(errorData.detail || 'Failed to generate DOCX');
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' }));
      const link = document.createElement('a');
      link.href = url;
      const safeFilename = `seo-audit-${(audit?.website_url || 'report').replace(/[^a-z0-9]/gi, '-')}.docx`;
      link.setAttribute('download', safeFilename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast({
        title: "Success!",
        description: "DOCX report downloaded successfully.",
      });
    } catch (error) {
      console.error('Error downloading DOCX:', error);
      toast({
        title: "Download Failed",
        description: error.message || error.response?.data?.detail || "Failed to download DOCX report. Please try again.",
        variant: "destructive",
      });
    } finally {
      setDownloadingDocx(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Loader2 className="w-12 h-12 animate-spin" style={{ color: 'var(--apollo-primary)' }} />
      </div>
    );
  }

  if (!audit) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
        <ApolloNavbar />
        <div className="apollo-container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
          <div className="apollo-card" style={{ padding: '3rem', maxWidth: '600px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--apollo-gray-900)', marginBottom: '1rem' }}>
              Audit not found
            </h2>
            <p style={{ color: 'var(--apollo-gray-600)', marginBottom: '1.5rem' }}>
              The audit you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <Button onClick={() => navigate('/dashboard')} className="apollo-btn apollo-btn-primary">
              Back to Dashboard
            </Button>
          </div>
        </div>
        <ApolloFooter />
      </div>
    );
  }

  const groupedResults = audit.results ? groupResultsByCategory(audit.results) : {};

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />

      <div className="apollo-container" style={{ padding: '2rem 1.5rem' }} data-testid="audit-detail">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          className="apollo-navbar-link"
          onClick={() => navigate('/dashboard')}
          style={{ marginBottom: '1.5rem', display: 'inline-flex' }}
        >
          <ArrowLeft className="w-4 h-4" style={{ marginRight: '0.5rem' }} />
          Back to Dashboard
        </Button>

        {/* Header Card */}
        <div className="apollo-card apollo-fade-in" style={{ padding: '2rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '2rem' }}>
            <div style={{ flex: '1', minWidth: '300px' }}>
              <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: 'var(--apollo-gray-900)', marginBottom: '1rem' }}>
                {audit.website_url}
              </h1>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', color: 'var(--apollo-gray-600)', fontSize: '0.875rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Globe className="w-4 h-4" />
                  {audit.pages_crawled} pages crawled
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Clock className="w-4 h-4" />
                  {audit.total_checks_run} checks completed
                </div>
              </div>
              {polling && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--apollo-primary)', marginTop: '1rem' }}>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span style={{ fontSize: '0.875rem' }}>Processing audit... Status: {audit.status.replace('_', ' ')}</span>
                </div>
              )}
            </div>
            {audit.overall_score !== null && (
              <div style={{ textAlign: 'center', padding: '1rem' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--apollo-gray-600)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                  Overall SEO Score
                </div>
                <div style={{ fontSize: '4rem', fontWeight: 700, color: getScoreColor(audit.overall_score), lineHeight: 1 }}>
                  {audit.overall_score}
                </div>
                <div style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-500)', marginTop: '0.25rem' }}>
                  / 100
                </div>
                <Progress 
                  value={audit.overall_score} 
                  className="mt-4"
                  style={{ width: '120px', margin: '1rem auto 0' }}
                />
              </div>
            )}
          </div>

          {audit.overall_score !== null && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5rem', marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid var(--apollo-gray-200)' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--apollo-success)' }}>{audit.checks_passed}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-600)' }}>Passed</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--apollo-error)' }}>{audit.checks_failed}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-600)' }}>Failed</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--apollo-warning)' }}>{audit.checks_warning}</div>
                  <div style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-600)' }}>Warnings</div>
                </div>
              </div>

              {/* Action Buttons - HIGHLY VISIBLE */}
              {audit.status === 'completed' && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '2rem', paddingTop: '2rem', borderTop: '1px solid var(--apollo-gray-200)' }}>
                  <button
                    onClick={handleDownloadPdf}
                    disabled={downloadingPdf}
                    className="apollo-btn apollo-btn-primary"
                    style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.95rem' }}
                  >
                    {downloadingPdf ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Generating PDF...
                      </>
                    ) : (
                      <>
                        <Download className="w-5 h-5" />
                        Download PDF
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDownloadDocx}
                    disabled={downloadingDocx}
                    className="apollo-btn apollo-btn-secondary"
                    style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.95rem' }}
                  >
                    {downloadingDocx ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Generating DOCX...
                      </>
                    ) : (
                      <>
                        <FileText className="w-5 h-5" />
                        Download DOCX
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => navigate(`/chat/${id}`)}
                    className="apollo-btn"
                    style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.95rem', background: 'var(--apollo-success)', color: 'white' }}
                  >
                    <MessageCircle className="w-5 h-5" />
                    Chat with AI
                  </button>

                  <button
                    onClick={() => navigate(`/audit/${id}/competitors`)}
                    className="apollo-btn"
                    style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.95rem', background: 'var(--apollo-primary)', color: 'white' }}
                  >
                    <TrendingUp className="w-5 h-5" />
                    View Competitors {audit.competitor_count > 0 && `(${audit.competitor_count})`}
                  </button>

                  <button
                    onClick={() => navigate(`/audit/${id}/opportunities`)}
                    className="apollo-btn"
                    style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '0.95rem', background: '#f59e0b', color: 'white' }}
                  >
                    <BarChart3 className="w-5 h-5" />
                    Content Ideas {audit.opportunities_found > 0 && `(${audit.opportunities_found})`}
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Results by Category */}
        {audit.results && audit.results.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--apollo-gray-900)', marginBottom: '0.5rem' }}>
              Detailed Check Results
            </h2>
            {Object.entries(groupedResults).map(([category, results]) => (
              <div key={category} className="apollo-card apollo-fade-in">
                <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--apollo-gray-200)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', justifyContent: 'space-between', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      {getCategoryIcon(category)}
                      <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--apollo-gray-900)' }}>
                        {category}
                      </h3>
                    </div>
                    <span className="apollo-badge apollo-badge-info">
                      {results.length} checks
                    </span>
                  </div>
                </div>
                <div style={{ padding: '1rem' }}>
                  <Accordion type="single" collapsible className="space-y-2">
                    {results.map((result, index) => (
                      <AccordionItem 
                        key={result.id} 
                        value={`item-${index}`} 
                        style={{ border: '1px solid var(--apollo-gray-200)', borderRadius: 'var(--apollo-radius)', padding: '0 1rem' }}
                      >
                        <AccordionTrigger className="hover:no-underline">
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1, textAlign: 'left' }}>
                            {getStatusIcon(result.status)}
                            <span style={{ color: 'var(--apollo-gray-900)', fontWeight: 500 }}>{result.check_name}</span>
                            {result.impact_score && (
                              <span className="apollo-badge" style={{ marginLeft: 'auto', marginRight: '1rem', background: 'var(--apollo-info-light)', color: 'var(--apollo-info)' }}>
                                Impact: {result.impact_score}/100
                              </span>
                            )}
                          </div>
                        </AccordionTrigger>
                        <AccordionContent style={{ color: 'var(--apollo-gray-700)', paddingTop: '1rem' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            {result.current_value && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-gray-600)', marginBottom: '0.25rem' }}>
                                  Current Value:
                                </div>
                                <div style={{ color: 'var(--apollo-gray-900)' }}>{result.current_value}</div>
                              </div>
                            )}
                            {result.recommended_value && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-gray-600)', marginBottom: '0.25rem' }}>
                                  Recommended:
                                </div>
                                <div style={{ color: 'var(--apollo-gray-900)' }}>{result.recommended_value}</div>
                              </div>
                            )}
                            {result.pros && result.pros.length > 0 && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-success)', marginBottom: '0.5rem' }}>
                                  ✅ Pros:
                                </div>
                                <ul style={{ listStyle: 'disc', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                  {result.pros.map((pro, i) => <li key={i} style={{ color: 'var(--apollo-gray-700)' }}>{pro}</li>)}
                                </ul>
                              </div>
                            )}
                            {result.cons && result.cons.length > 0 && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-error)', marginBottom: '0.5rem' }}>
                                  ❌ Cons:
                                </div>
                                <ul style={{ listStyle: 'disc', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                  {result.cons.map((con, i) => <li key={i} style={{ color: 'var(--apollo-gray-700)' }}>{con}</li>)}
                                </ul>
                              </div>
                            )}
                            {result.ranking_impact && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-warning)', marginBottom: '0.25rem' }}>
                                  📊 Ranking Impact:
                                </div>
                                <div style={{ color: 'var(--apollo-gray-700)' }}>{result.ranking_impact}</div>
                              </div>
                            )}
                            {result.solution && (
                              <div style={{ background: 'var(--apollo-info-light)', border: '1px solid var(--apollo-info)', borderRadius: 'var(--apollo-radius)', padding: '1rem' }}>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-info)', marginBottom: '0.5rem' }}>
                                  💡 Solution:
                                </div>
                                <div style={{ color: 'var(--apollo-gray-900)', whiteSpace: 'pre-wrap' }}>{result.solution}</div>
                              </div>
                            )}
                            {result.enhancements && result.enhancements.length > 0 && (
                              <div>
                                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--apollo-secondary)', marginBottom: '0.5rem' }}>
                                  🚀 Enhancement Suggestions:
                                </div>
                                <ul style={{ listStyle: 'disc', paddingLeft: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                  {result.enhancements.map((enh, i) => <li key={i} style={{ color: 'var(--apollo-gray-700)' }}>{enh}</li>)}
                                </ul>
                              </div>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ApolloFooter />
    </div>
  );
};

export default AuditDetail;
