import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

const CompetitorsPage = () => {
  const { auditId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [competitors, setCompetitors] = useState([]);
  const [selectedCompetitor, setSelectedCompetitor] = useState(null);
  const [showKeywordGaps, setShowKeywordGaps] = useState(false);
  const [keywordGaps, setKeywordGaps] = useState([]);
  const [audit, setAudit] = useState(null);

  useEffect(() => {
    fetchAuditAndCompetitors();
  }, [auditId]);

  const fetchAuditAndCompetitors = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch audit details
      const auditResponse = await axios.get(`${API_URL}/audits/${auditId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAudit(auditResponse.data);

      // Fetch competitors
      const competitorsResponse = await axios.get(
        `${API_URL}/audits/${auditId}/competitors`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCompetitors(competitorsResponse.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching competitors:', error);
      toast.error('Failed to load competitors');
      setLoading(false);
    }
  };

  const viewKeywordGaps = async (competitorId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/audits/${auditId}/competitors/${competitorId}/keyword-gaps`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setKeywordGaps(response.data.keyword_gaps || []);
      setShowKeywordGaps(true);
      setSelectedCompetitor(competitors.find(c => c.id === competitorId));
    } catch (error) {
      console.error('Error fetching keyword gaps:', error);
      toast.error('Failed to load keyword gaps');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading competitors...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate(`/audit/${auditId}`)}
                className="text-sm text-gray-500 hover:text-gray-700 mb-2 flex items-center"
              >
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Audit
              </button>
              <h1 className="text-3xl font-bold text-gray-900">Competitor Analysis</h1>
              <p className="mt-2 text-gray-600">
                {audit?.website_url} • {competitors.length} competitors identified
              </p>
            </div>
            <div className="bg-indigo-50 px-4 py-3 rounded-lg">
              <div className="text-sm text-gray-600">Your Score</div>
              <div className="text-3xl font-bold text-indigo-600">{audit?.overall_score || 0}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {competitors.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Competitors Found</h3>
            <p className="text-gray-600 mb-4">
              No competitor data available yet. Competitors will be automatically discovered during the audit process.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Competitors Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {competitors.map((competitor, index) => (
                <div
                  key={competitor.id}
                  className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200 overflow-hidden"
                >
                  {/* Rank Badge */}
                  <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2">
                    <div className="flex items-center justify-between text-white">
                      <span className="text-sm font-medium">Rank #{index + 1}</span>
                      {competitor.domain_authority && (
                        <span className="text-sm">DA: {Math.round(competitor.domain_authority)}</span>
                      )}
                    </div>
                  </div>

                  {/* Competitor Info */}
                  <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 truncate" title={competitor.competitor_url}>
                      {competitor.competitor_domain || competitor.competitor_url}
                    </h3>

                    <div className="space-y-3">
                      {/* Score Comparison */}
                      {competitor.competitor_score && (
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-gray-600">SEO Score</span>
                            <span className="font-medium">{Math.round(competitor.competitor_score)}/100</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{ width: `${competitor.competitor_score}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      {/* Stats Grid */}
                      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100">
                        {competitor.backlink_count !== null && (
                          <div>
                            <div className="text-xs text-gray-500">Backlinks</div>
                            <div className="text-lg font-semibold text-gray-900">
                              {competitor.backlink_count?.toLocaleString() || '0'}
                            </div>
                          </div>
                        )}
                        {competitor.referring_domains !== null && (
                          <div>
                            <div className="text-xs text-gray-500">Referring Domains</div>
                            <div className="text-lg font-semibold text-gray-900">
                              {competitor.referring_domains?.toLocaleString() || '0'}
                            </div>
                          </div>
                        )}
                        {competitor.organic_traffic_estimate !== null && (
                          <div className="col-span-2">
                            <div className="text-xs text-gray-500">Est. Organic Traffic</div>
                            <div className="text-lg font-semibold text-gray-900">
                              {competitor.organic_traffic_estimate?.toLocaleString() || '0'}/mo
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="mt-6 pt-4 border-t border-gray-100 space-y-2">
                      <button
                        onClick={() => viewKeywordGaps(competitor.id)}
                        className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                      >
                        View Keyword Gaps
                      </button>
                      <a
                        href={competitor.competitor_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-full block text-center text-indigo-600 hover:text-indigo-700 px-4 py-2 text-sm font-medium"
                      >
                        Visit Website →
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Keyword Gaps Modal */}
      {showKeywordGaps && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Keyword Gaps</h2>
                  <p className="text-gray-600 mt-1">
                    Keywords that {selectedCompetitor?.competitor_domain} ranks for, but you don't
                  </p>
                </div>
                <button
                  onClick={() => setShowKeywordGaps(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {keywordGaps.length === 0 ? (
                <p className="text-gray-600 text-center py-8">No keyword gaps data available</p>
              ) : (
                <div className="space-y-3">
                  {keywordGaps.slice(0, 50).map((gap, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{gap.keyword || gap}</h4>
                        {gap.search_volume && (
                          <p className="text-sm text-gray-600 mt-1">
                            Volume: {gap.search_volume?.toLocaleString()}/mo
                            {gap.difficulty && ` • Difficulty: ${Math.round(gap.difficulty)}/100`}
                          </p>
                        )}
                      </div>
                      {gap.search_volume && gap.difficulty && (
                        <div className="ml-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            gap.difficulty < 30 ? 'bg-green-100 text-green-800' :
                            gap.difficulty < 60 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {gap.difficulty < 30 ? 'Easy' : gap.difficulty < 60 ? 'Medium' : 'Hard'}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setShowKeywordGaps(false)}
                className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CompetitorsPage;
