import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

const ContentOpportunitiesPage = () => {
  const { auditId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [opportunities, setOpportunities] = useState([]);
  const [filteredOpportunities, setFilteredOpportunities] = useState([]);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [showBriefModal, setShowBriefModal] = useState(false);
  const [generatingBrief, setGeneratingBrief] = useState(false);
  const [filter, setFilter] = useState('all');
  const [audit, setAudit] = useState(null);

  useEffect(() => {
    fetchOpportunities();
  }, [auditId]);

  useEffect(() => {
    filterOpportunities();
  }, [opportunities, filter]);

  const fetchOpportunities = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch audit details
      const auditResponse = await axios.get(`${API_URL}/audits/${auditId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAudit(auditResponse.data);

      // Fetch opportunities
      const opportunitiesResponse = await axios.get(
        `${API_URL}/audits/${auditId}/opportunities`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setOpportunities(opportunitiesResponse.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching opportunities:', error);
      toast.error('Failed to load content opportunities');
      setLoading(false);
    }
  };

  const filterOpportunities = () => {
    let filtered = [...opportunities];
    
    if (filter === 'high-priority') {
      filtered = filtered.filter(opp => opp.priority_score && opp.priority_score >= 70);
    } else if (filter === 'quick-wins') {
      filtered = filtered.filter(opp => 
        opp.keyword_difficulty && opp.keyword_difficulty < 30 && 
        opp.search_volume && opp.search_volume > 100
      );
    } else if (filter === 'pending') {
      filtered = filtered.filter(opp => opp.status === 'pending');
    }
    
    // Sort by priority score
    filtered.sort((a, b) => (b.priority_score || 0) - (a.priority_score || 0));
    
    setFilteredOpportunities(filtered);
  };

  const generateContentBrief = async (opportunityId) => {
    try {
      setGeneratingBrief(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/audits/${auditId}/opportunities/${opportunityId}/generate-brief`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Refresh the opportunity to get the new brief
      const oppResponse = await axios.get(
        `${API_URL}/audits/${auditId}/opportunities/${opportunityId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSelectedOpportunity(oppResponse.data);
      toast.success('Content brief generated successfully!');
    } catch (error) {
      console.error('Error generating brief:', error);
      toast.error('Failed to generate content brief');
    } finally {
      setGeneratingBrief(false);
    }
  };

  const viewOpportunityDetail = async (opportunityId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/audits/${auditId}/opportunities/${opportunityId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSelectedOpportunity(response.data);
      setShowBriefModal(true);
    } catch (error) {
      console.error('Error fetching opportunity details:', error);
      toast.error('Failed to load opportunity details');
    }
  };

  const updateStatus = async (opportunityId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/audits/${auditId}/opportunities/${opportunityId}/status?status=${newStatus}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Status updated');
      fetchOpportunities();
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Failed to update status');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading opportunities...</p>
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
              <h1 className="text-3xl font-bold text-gray-900">Content Opportunities</h1>
              <p className="mt-2 text-gray-600">
                {audit?.website_url} • {opportunities.length} opportunities found
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex space-x-2">
            {[
              { value: 'all', label: 'All Opportunities' },
              { value: 'high-priority', label: 'High Priority' },
              { value: 'quick-wins', label: 'Quick Wins' },
              { value: 'pending', label: 'Pending' }
            ].map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setFilter(value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === value
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredOpportunities.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Opportunities Found</h3>
            <p className="text-gray-600">
              {filter !== 'all' ? 'Try adjusting your filters' : 'Content opportunities will be generated during the audit process'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredOpportunities.map((opportunity) => (
              <div
                key={opportunity.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200 p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {opportunity.keyword || 'Opportunity'}
                      </h3>
                      {opportunity.priority_score && (
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          opportunity.priority_score >= 70 ? 'bg-red-100 text-red-800' :
                          opportunity.priority_score >= 40 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          Priority: {Math.round(opportunity.priority_score)}
                        </span>
                      )}
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        opportunity.status === 'completed' ? 'bg-green-100 text-green-800' :
                        opportunity.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {opportunity.status?.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      {opportunity.search_volume && (
                        <div>
                          <div className="text-xs text-gray-500">Search Volume</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {opportunity.search_volume.toLocaleString()}/mo
                          </div>
                        </div>
                      )}
                      {opportunity.keyword_difficulty !== null && (
                        <div>
                          <div className="text-xs text-gray-500">Difficulty</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {Math.round(opportunity.keyword_difficulty)}/100
                          </div>
                        </div>
                      )}
                      {opportunity.potential_traffic && (
                        <div>
                          <div className="text-xs text-gray-500">Potential Traffic</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {opportunity.potential_traffic.toLocaleString()}/mo
                          </div>
                        </div>
                      )}
                      {opportunity.estimated_effort_hours && (
                        <div>
                          <div className="text-xs text-gray-500">Est. Effort</div>
                          <div className="text-lg font-semibold text-gray-900">
                            {opportunity.estimated_effort_hours}h
                          </div>
                        </div>
                      )}
                    </div>

                    {opportunity.competition_level && (
                      <p className="text-sm text-gray-600 mb-4">
                        Competition: <span className="font-medium capitalize">{opportunity.competition_level}</span>
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-3 pt-4 border-t border-gray-100">
                  <button
                    onClick={() => viewOpportunityDetail(opportunity.id)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                  >
                    View Details
                  </button>
                  {opportunity.status === 'pending' && (
                    <button
                      onClick={() => updateStatus(opportunity.id, 'in_progress')}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      Start Working
                    </button>
                  )}
                  {opportunity.status === 'in_progress' && (
                    <button
                      onClick={() => updateStatus(opportunity.id, 'completed')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Mark Complete
                    </button>
                  )}
                  <button
                    onClick={() => updateStatus(opportunity.id, 'dismissed')}
                    className="text-gray-600 hover:text-gray-800 px-4 py-2 text-sm font-medium"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showBriefModal && selectedOpportunity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">{selectedOpportunity.keyword}</h2>
                <button
                  onClick={() => setShowBriefModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
              {selectedOpportunity.content_brief ? (
                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700">{selectedOpportunity.content_brief}</div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">No content brief generated yet</p>
                  <button
                    onClick={() => generateContentBrief(selectedOpportunity.id)}
                    disabled={generatingBrief}
                    className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50"
                  >
                    {generatingBrief ? 'Generating...' : 'Generate AI Content Brief'}
                  </button>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setShowBriefModal(false)}
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

export default ContentOpportunitiesPage;
