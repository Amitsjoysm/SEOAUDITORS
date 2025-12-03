import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/api/axios';
import { Toaster, toast } from 'react-hot-toast';

const IntegrationsDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [integrations, setIntegrations] = useState([]);
  const [overview, setOverview] = useState(null);
  const [testing, setTesting] = useState({});

  useEffect(() => {
    fetchIntegrations();
    fetchOverview();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const response = await api.get('/admin/integrations/');
      setIntegrations(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching integrations:', error);
      if (error.response?.status === 403) {
        toast.error('Admin access required');
        navigate('/dashboard');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to load integrations');
      }
      setLoading(false);
    }
  };

  const fetchOverview = async () => {
    try {
      const response = await api.get('/admin/integrations/dashboard/overview');
      setOverview(response.data);
    } catch (error) {
      console.error('Error fetching overview:', error);
    }
  };

  const testIntegration = async (serviceName) => {
    try {
      setTesting(prev => ({ ...prev, [serviceName]: true }));
      const response = await api.post(`/admin/integrations/test/${serviceName}`, {});
      
      if (response.data.success) {
        toast.success(`${serviceName} test passed!`);
      } else {
        toast.error(`${serviceName} test failed: ${response.data.error}`);
      }
      
      // Refresh integrations
      fetchIntegrations();
    } catch (error) {
      console.error('Error testing integration:', error);
      toast.error(error.response?.data?.detail || 'Failed to test integration');
    } finally {
      setTesting(prev => ({ ...prev, [serviceName]: false }));
    }
  };

  const getStatusColor = (isHealthy) => {
    return isHealthy ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  };

  const getStatusIcon = (isHealthy) => {
    return isHealthy ? (
      <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
      </svg>
    ) : (
      <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    );
  };

  const getServiceDisplayName = (serviceName) => {
    const names = {
      'dataforseo': 'DataForSEO',
      'lighthouse': 'Lighthouse CLI',
      'google_search_console': 'Google Search Console',
      'google_analytics': 'Google Analytics',
      'exa_ai': 'Exa.ai',
      'groq': 'Groq',
      'openai': 'OpenAI',
      'anthropic': 'Anthropic',
      'gemini': 'Google Gemini'
    };
    return names[serviceName] || serviceName;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading integrations...</p>
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
              <h1 className="text-3xl font-bold text-gray-900">Integrations Dashboard</h1>
              <p className="mt-2 text-gray-600">Monitor API health and performance</p>
            </div>
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      {overview && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Services</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{overview.summary.total_services}</p>
                </div>
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Healthy Services</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">{overview.summary.healthy_services}</p>
                </div>
                <div className="bg-green-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Overall Uptime</p>
                  <p className="text-3xl font-bold text-indigo-600 mt-1">{overview.summary.overall_uptime_percentage}%</p>
                </div>
                <div className="bg-indigo-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Requests Today</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{overview.summary.total_requests_today}</p>
                </div>
                <div className="bg-blue-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Integrations List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">API Services</h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {integrations.map((integration) => (
              <div key={integration.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      {getStatusIcon(integration.is_healthy)}
                      <h3 className="text-lg font-semibold text-gray-900">
                        {getServiceDisplayName(integration.service_name)}
                      </h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(integration.is_healthy)}`}>
                        {integration.is_healthy ? 'Healthy' : 'Unhealthy'}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <div className="text-xs text-gray-500">Uptime (24h)</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {integration.uptime_percentage?.toFixed(1) || 0}%
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Success Rate</div>
                        <div className="text-lg font-semibold text-green-600">
                          {integration.success_count_24h}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Failures</div>
                        <div className="text-lg font-semibold text-red-600">
                          {integration.failure_count_24h}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500">Avg Response</div>
                        <div className="text-lg font-semibold text-gray-900">
                          {integration.avg_response_time_ms ? `${Math.round(integration.avg_response_time_ms)}ms` : 'N/A'}
                        </div>
                      </div>
                    </div>

                    {integration.error_message && (
                      <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                        <p className="text-sm text-red-800">
                          <span className="font-medium">Last Error:</span> {integration.error_message}
                        </p>
                        {integration.last_error_at && (
                          <p className="text-xs text-red-600 mt-1">
                            {new Date(integration.last_error_at).toLocaleString()}
                          </p>
                        )}
                      </div>
                    )}

                    {integration.last_check_at && (
                      <p className="text-sm text-gray-500">
                        Last checked: {new Date(integration.last_check_at).toLocaleString()}
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() => testIntegration(integration.service_name)}
                    disabled={testing[integration.service_name]}
                    className="ml-4 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {testing[integration.service_name] ? 'Testing...' : 'Test'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntegrationsDashboard;