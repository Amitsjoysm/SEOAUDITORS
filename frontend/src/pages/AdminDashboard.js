import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import axios from '@/api/axios';
import {
  Users, FileText, CreditCard, Settings, BarChart3,
  Plus, Edit, Trash2, Check, X, Palette, ArrowLeft, Key, Eye, EyeOff, Copy
} from 'lucide-react';

const AdminDashboard = () => {
  const { user } = useAuth();
  const { theme, refreshTheme } = useTheme();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [plans, setPlans] = useState([]);
  const [themes, setThemes] = useState([]);
  const [audits, setAudits] = useState([]);
  const [envKeys, setEnvKeys] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [editingTheme, setEditingTheme] = useState(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [editingKey, setEditingKey] = useState(null);
  const [showKeyValue, setShowKeyValue] = useState({});
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [llmSettings, setLlmSettings] = useState([]);
  const [showLlmModal, setShowLlmModal] = useState(false);
  const [editingLlm, setEditingLlm] = useState(null);
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    if (user?.role !== 'superadmin') {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, usersRes, plansRes, themesRes, auditsRes, envKeysRes, llmRes] = await Promise.all([
        axios.get('/admin/stats'),
        axios.get('/admin/users'),
        axios.get('/plans/'),
        axios.get('/themes/'),
        axios.get('/admin/audits'),
        axios.get('/admin/env-keys'),
        axios.get('/admin/llm-settings/')
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setPlans(plansRes.data);
      setThemes(themesRes.data);
      setAudits(auditsRes.data);
      setEnvKeys(envKeysRes.data);
      setLlmSettings(llmRes.data);
      console.log('Admin data loaded successfully:', {
        stats: statsRes.data,
        usersCount: usersRes.data.length,
        plansCount: plansRes.data.length,
        themesCount: themesRes.data.length,
        auditsCount: auditsRes.data.length,
        envKeysCount: envKeysRes.data.length,
        llmCount: llmRes.data.length
      });
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const handleActivateTheme = async (themeId) => {
    try {
      await axios.post(`/themes/${themeId}/activate`);
      await refreshTheme();
      fetchData();
      alert('Theme activated successfully!');
    } catch (error) {
      console.error('Failed to activate theme:', error);
      alert('Failed to activate theme');
    }
  };

  const handleCreateTheme = async (themeData) => {
    try {
      await axios.post('/themes/', themeData);
      fetchData();
      setShowThemeModal(false);
      alert('Theme created successfully!');
    } catch (error) {
      console.error('Failed to create theme:', error);
      alert(error.response?.data?.detail || 'Failed to create theme');
    }
  };

  const handleUpdateTheme = async (themeId, themeData) => {
    try {
      await axios.put(`/themes/${themeId}`, themeData);
      fetchData();
      setEditingTheme(null);
      setShowThemeModal(false);
      alert('Theme updated successfully!');
    } catch (error) {
      console.error('Failed to update theme:', error);
      alert(error.response?.data?.detail || 'Failed to update theme');
    }
  };

  const handleDeleteTheme = async (themeId) => {
    if (!window.confirm('Are you sure you want to delete this theme?')) return;
    
    try {
      await axios.delete(`/themes/${themeId}`);
      fetchData();
      alert('Theme deleted successfully');
    } catch (error) {
      console.error('Failed to delete theme:', error);
      alert(error.response?.data?.detail || 'Failed to delete theme');
    }
  };

  const handleActivateLlm = async (llmId) => {
    try {
      await axios.post(`/admin/llm-settings/${llmId}/activate`);
      fetchData();
      alert('LLM setting activated successfully!');
    } catch (error) {
      console.error('Failed to activate LLM:', error);
      alert('Failed to activate LLM setting');
    }
  };

  const handleCreateLlm = async (llmData) => {
    try {
      await axios.post('/admin/llm-settings/', llmData);
      fetchData();
      setShowLlmModal(false);
      alert('LLM setting created successfully!');
    } catch (error) {
      console.error('Failed to create LLM setting:', error);
      alert(error.response?.data?.detail || 'Failed to create LLM setting');
    }
  };

  const handleUpdateLlm = async (llmId, llmData) => {
    try {
      await axios.put(`/admin/llm-settings/${llmId}`, llmData);
      fetchData();
      setEditingLlm(null);
      setShowLlmModal(false);
      alert('LLM setting updated successfully!');
    } catch (error) {
      console.error('Failed to update LLM setting:', error);
      alert(error.response?.data?.detail || 'Failed to update LLM setting');
    }
  };

  const handleDeleteLlm = async (llmId) => {
    if (!window.confirm('Are you sure you want to delete this LLM setting?')) return;
    
    try {
      await axios.delete(`/admin/llm-settings/${llmId}`);
      fetchData();
      alert('LLM setting deleted successfully');
    } catch (error) {
      console.error('Failed to delete LLM setting:', error);
      alert(error.response?.data?.detail || 'Failed to delete LLM setting');
    }
  };

  const fetchModelsForProvider = async (provider) => {
    try {
      const response = await axios.get(`/admin/llm-settings/models/${provider}`);
      setAvailableModels(response.data.models || []);
    } catch (error) {
      console.error('Failed to fetch models:', error);
      setAvailableModels([]);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      await axios.delete(`/admin/users/${userId}`);
      fetchData();
      alert('User deleted successfully');
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('Failed to delete user');
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      await axios.put(`/admin/users/${userId}`, { is_active: !currentStatus });
      fetchData();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  const handleCreateKey = async (keyData) => {
    try {
      await axios.post('/admin/env-keys', keyData);
      fetchData();
      setShowKeyModal(false);
      alert('Environment key created successfully');
    } catch (error) {
      console.error('Failed to create key:', error);
      alert(error.response?.data?.detail || 'Failed to create key');
    }
  };

  const handleUpdateKey = async (keyId, keyData) => {
    try {
      await axios.put(`/admin/env-keys/${keyId}`, keyData);
      fetchData();
      setEditingKey(null);
      setShowKeyModal(false);
      alert('Environment key updated successfully');
    } catch (error) {
      console.error('Failed to update key:', error);
      alert(error.response?.data?.detail || 'Failed to update key');
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (!window.confirm('Are you sure you want to delete this environment key?')) return;
    
    try {
      await axios.delete(`/admin/env-keys/${keyId}`);
      fetchData();
      alert('Environment key deleted successfully');
    } catch (error) {
      console.error('Failed to delete key:', error);
      alert('Failed to delete key');
    }
  };

  const handleToggleKeyVisibility = async (keyId) => {
    if (showKeyValue[keyId]) {
      setShowKeyValue({ ...showKeyValue, [keyId]: null });
      return;
    }

    try {
      const response = await axios.get(`/admin/env-keys/${keyId}`);
      setShowKeyValue({ ...showKeyValue, [keyId]: response.data.key_value });
    } catch (error) {
      console.error('Failed to fetch key value:', error);
      alert('Failed to fetch key value');
    }
  };

  const handleCopyKey = (value) => {
    navigator.clipboard.writeText(value);
    alert('Key copied to clipboard!');
  };

  const handleInitializeDefaults = async () => {
    try {
      const response = await axios.post('/admin/env-keys/initialize-defaults');
      fetchData();
      alert(response.data.message);
    } catch (error) {
      console.error('Failed to initialize defaults:', error);
      alert('Failed to initialize default keys');
    }
  };

  const handleUpdatePlan = async (planId, planData) => {
    try {
      await axios.put(`/plans/${planId}`, planData);
      fetchData();
      setEditingPlan(null);
      setShowPlanModal(false);
      alert('Plan updated successfully!');
    } catch (error) {
      console.error('Failed to update plan:', error);
      alert(error.response?.data?.detail || 'Failed to update plan');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading admin dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-8 max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-4">Error Loading Dashboard</h2>
          <p className="text-gray-300 mb-4">{error}</p>
          <button
            onClick={() => fetchData()}
            className="px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Header */}
      <div className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-800">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <h1 className="text-3xl font-bold text-white">Super Admin Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-400">Welcome, {user?.full_name || user?.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="container mx-auto px-4 py-6">
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'users', label: 'Users', icon: Users },
            { id: 'plans', label: 'Plans', icon: CreditCard },
            { id: 'themes', label: 'Themes', icon: Palette },
            { id: 'audits', label: 'Audits', icon: FileText },
            { id: 'env-keys', label: 'Environment Keys', icon: Key }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/50'
                  : 'bg-slate-800 text-gray-400 hover:bg-slate-700'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <Users className="w-8 h-8 text-purple-400" />
                <span className="text-3xl font-bold text-white">{stats.total_users}</span>
              </div>
              <h3 className="text-gray-400">Total Users</h3>
            </div>
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <FileText className="w-8 h-8 text-blue-400" />
                <span className="text-3xl font-bold text-white">{stats.total_audits}</span>
              </div>
              <h3 className="text-gray-400">Total Audits</h3>
            </div>
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <CreditCard className="w-8 h-8 text-green-400" />
                <span className="text-3xl font-bold text-white">{stats.active_subscriptions}</span>
              </div>
              <h3 className="text-gray-400">Active Subscriptions</h3>
            </div>
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <FileText className="w-8 h-8 text-pink-400" />
                <span className="text-3xl font-bold text-white">{stats.audits_today}</span>
              </div>
              <h3 className="text-gray-400">Audits Today</h3>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Email</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Name</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Role</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Created</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-300">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 text-sm text-white">{u.email}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{u.full_name || '-'}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          u.role === 'superadmin' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <button
                          onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                          className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            u.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {u.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {u.role !== 'superadmin' && (
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="text-red-400 hover:text-red-300 transition-colors"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Plans Tab */}
        {activeTab === 'plans' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {plans.map((plan) => (
              <div key={plan.id} className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800 relative">
                <button
                  onClick={() => { setEditingPlan(plan); setShowPlanModal(true); }}
                  className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                  title="Edit Plan"
                >
                  <Edit className="w-5 h-5" />
                </button>
                <h3 className="text-2xl font-bold text-white mb-2">{plan.display_name}</h3>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                <div className="text-3xl font-bold text-white mb-4">${plan.price}/mo</div>
                <div className="space-y-2 mb-4">
                  <div className="text-sm text-gray-300">
                    <strong>Max Audits:</strong> {plan.max_audits_per_month === 999999 ? 'Unlimited' : plan.max_audits_per_month}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Pages per Audit:</strong> {plan.max_pages_per_audit}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Stripe Price ID:</strong>
                    <div className="mt-1 font-mono text-xs bg-slate-800 px-2 py-1 rounded text-purple-400 break-all">
                      {plan.stripe_price_id || 'Not set'}
                    </div>
                  </div>
                </div>
                <div className="text-sm">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    plan.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Plan Edit Modal */}
        {showPlanModal && editingPlan && (
          <PlanModal
            plan={editingPlan}
            onClose={() => { setShowPlanModal(false); setEditingPlan(null); }}
            onUpdate={handleUpdatePlan}
          />
        )}

        {/* Themes Tab */}
        {activeTab === 'themes' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {themes.map((t) => (
              <div key={t.id} className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800 relative">
                {t.is_active && (
                  <div className="absolute top-4 right-4">
                    <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      Active
                    </div>
                  </div>
                )}
                <h3 className="text-xl font-bold text-white mb-4">{t.name}</h3>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Primary</div>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg border-2 border-gray-700" style={{ backgroundColor: t.primary_color }}></div>
                      <span className="text-xs text-gray-300">{t.primary_color}</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Secondary</div>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg border-2 border-gray-700" style={{ backgroundColor: t.secondary_color }}></div>
                      <span className="text-xs text-gray-300">{t.secondary_color}</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Accent</div>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg border-2 border-gray-700" style={{ backgroundColor: t.accent_color }}></div>
                      <span className="text-xs text-gray-300">{t.accent_color}</span>
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400 mb-1">Background</div>
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg border-2 border-gray-700" style={{ backgroundColor: t.background_color }}></div>
                      <span className="text-xs text-gray-300">{t.background_color}</span>
                    </div>
                  </div>
                </div>
                {!t.is_active && (
                  <button
                    onClick={() => handleActivateTheme(t.id)}
                    className="w-full py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-colors"
                  >
                    Activate Theme
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Audits Tab */}
        {activeTab === 'audits' && (
          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Website</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">User</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Score</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {audits.slice(0, 50).map((audit) => (
                    <tr key={audit.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 text-sm text-white">{audit.website_url}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">{audit.user_email}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          audit.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                          audit.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {audit.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-white">
                        {audit.overall_score ? `${Math.round(audit.overall_score)}%` : '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {new Date(audit.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Environment Keys Tab */}
        {activeTab === 'env-keys' && (
          <div>
            <div className="mb-6 flex gap-4">
              <button
                onClick={() => { setEditingKey(null); setShowKeyModal(true); }}
                className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Add New Key
              </button>
              <button
                onClick={handleInitializeDefaults}
                className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors"
              >
                Initialize from .env
              </button>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Key Name</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Category</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Description</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Value</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                      <th className="px-6 py-4 text-center text-sm font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {envKeys.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-6 py-12 text-center">
                          <p className="text-gray-400 mb-4">No environment keys found</p>
                          <button
                            onClick={handleInitializeDefaults}
                            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                          >
                            Initialize from .env
                          </button>
                        </td>
                      </tr>
                    ) : (
                      envKeys.map((key) => (
                      <tr key={key.id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="px-6 py-4 text-sm font-mono text-white">{key.key_name}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            key.category === 'payment' ? 'bg-green-500/20 text-green-400' :
                            key.category === 'ai' ? 'bg-blue-500/20 text-blue-400' :
                            key.category === 'email' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {key.category || 'other'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300">{key.description || '-'}</td>
                        <td className="px-6 py-4 text-sm">
                          {showKeyValue[key.id] ? (
                            <div className="flex items-center gap-2">
                              <code className="text-xs bg-slate-800 px-2 py-1 rounded text-green-400 max-w-xs overflow-hidden text-ellipsis">
                                {showKeyValue[key.id]}
                              </code>
                              <button
                                onClick={() => handleCopyKey(showKeyValue[key.id])}
                                className="text-gray-400 hover:text-white"
                              >
                                <Copy className="w-4 h-4" />
                              </button>
                            </div>
                          ) : (
                            <span className="text-gray-500">••••••••••••</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                            key.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                          }`}>
                            {key.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleToggleKeyVisibility(key.id)}
                              className="text-blue-400 hover:text-blue-300 transition-colors"
                              title={showKeyValue[key.id] ? 'Hide value' : 'Show value'}
                            >
                              {showKeyValue[key.id] ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                            <button
                              onClick={() => { setEditingKey(key); setShowKeyModal(true); }}
                              className="text-yellow-400 hover:text-yellow-300 transition-colors"
                              title="Edit"
                            >
                              <Edit className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleDeleteKey(key.id)}
                              className="text-red-400 hover:text-red-300 transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    )))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Key Modal */}
            {showKeyModal && (
              <KeyModal
                key={editingKey?.id || 'new'}
                editingKey={editingKey}
                onClose={() => { setShowKeyModal(false); setEditingKey(null); }}
                onCreate={handleCreateKey}
                onUpdate={handleUpdateKey}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// KeyModal Component
const KeyModal = ({ editingKey, onClose, onCreate, onUpdate }) => {
  const [formData, setFormData] = React.useState({
    key_name: editingKey?.key_name || '',
    key_value: '',
    description: editingKey?.description || '',
    category: editingKey?.category || 'other'
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editingKey) {
      onUpdate(editingKey.id, formData);
    } else {
      onCreate(formData);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 max-w-2xl w-full mx-4">
        <h2 className="text-2xl font-bold text-white mb-6">
          {editingKey ? 'Edit Environment Key' : 'Add New Environment Key'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Key Name</label>
            <input
              type="text"
              value={formData.key_name}
              onChange={(e) => setFormData({ ...formData, key_name: e.target.value })}
              disabled={!!editingKey}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 font-mono"
              placeholder="STRIPE_SECRET_KEY"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Key Value</label>
            <input
              type="password"
              value={formData.key_value}
              onChange={(e) => setFormData({ ...formData, key_value: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono"
              placeholder="Enter secret key value"
              required={!editingKey}
            />
            {editingKey && (
              <p className="text-xs text-gray-500 mt-1">Leave empty to keep existing value</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="payment">Payment</option>
              <option value="ai">AI</option>
              <option value="email">Email</option>
              <option value="database">Database</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows="3"
              placeholder="Describe what this key is used for..."
            />
          </div>
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-colors"
            >
              {editingKey ? 'Update Key' : 'Create Key'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );


// PlanModal Component
const PlanModal = ({ plan, onClose, onUpdate }) => {
  const [formData, setFormData] = React.useState({
    display_name: plan?.display_name || '',
    description: plan?.description || '',
    price: plan?.price || '',
    max_audits_per_month: plan?.max_audits_per_month || '',
    max_pages_per_audit: plan?.max_pages_per_audit || '',
    stripe_price_id: plan?.stripe_price_id || '',
    razorpay_plan_id: plan?.razorpay_plan_id || '',
    is_active: plan?.is_active !== undefined ? plan.is_active : false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const updateData = {
      ...formData,
      price: parseFloat(formData.price),
      max_audits_per_month: formData.max_audits_per_month === 'unlimited' ? 999999 : parseInt(formData.max_audits_per_month),
      max_pages_per_audit: parseInt(formData.max_pages_per_audit)
    };
    onUpdate(plan.id, updateData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-white mb-6">Edit Plan: {plan.name}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Display Name</label>
            <input
              type="text"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Pro Plan"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows="3"
              placeholder="Perfect for growing businesses..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Price (USD/month)</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="29.99"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Max Pages per Audit</label>
              <input
                type="number"
                value={formData.max_pages_per_audit}
                onChange={(e) => setFormData({ ...formData, max_pages_per_audit: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="10"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Max Audits per Month</label>
            <select
              value={formData.max_audits_per_month === 999999 ? 'unlimited' : formData.max_audits_per_month}
              onChange={(e) => setFormData({ ...formData, max_audits_per_month: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="2">2 audits</option>
              <option value="10">10 audits</option>
              <option value="25">25 audits</option>
              <option value="50">50 audits</option>
              <option value="100">100 audits</option>
              <option value="unlimited">Unlimited</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Stripe Price ID</label>
            <input
              type="text"
              value={formData.stripe_price_id}
              onChange={(e) => setFormData({ ...formData, stripe_price_id: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              placeholder="price_1234567890abcdef"
            />
            <p className="text-xs text-gray-500 mt-1">
              The Stripe Price ID for this plan. Get this from your Stripe Dashboard → Products → Prices
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Razorpay Plan ID (Optional)</label>
            <input
              type="text"
              value={formData.razorpay_plan_id}
              onChange={(e) => setFormData({ ...formData, razorpay_plan_id: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              placeholder="plan_1234567890abcdef"
            />
          </div>
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 text-purple-600 bg-slate-800 border-slate-700 rounded focus:ring-purple-500"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-300">
              Plan is active and available for subscription
            </label>
          </div>
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-colors"
            >
              Update Plan
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

};

// PlanModal Component
const PlanModal = ({ plan, onClose, onUpdate }) => {
  const [formData, setFormData] = React.useState({
    display_name: plan?.display_name || '',
    description: plan?.description || '',
    price: plan?.price || '',
    max_audits_per_month: plan?.max_audits_per_month || '',
    max_pages_per_audit: plan?.max_pages_per_audit || '',
    stripe_price_id: plan?.stripe_price_id || '',
    is_active: plan?.is_active || false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const updateData = {
      ...formData,
      price: parseFloat(formData.price),
      max_audits_per_month: formData.max_audits_per_month === 'unlimited' ? 999999 : parseInt(formData.max_audits_per_month),
      max_pages_per_audit: parseInt(formData.max_pages_per_audit)
    };
    onUpdate(plan.id, updateData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 rounded-xl border border-slate-800 p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-white mb-6">Edit Plan</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Display Name</label>
            <input
              type="text"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Pro Plan"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              rows="3"
              placeholder="Perfect for growing businesses..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Price (USD)</label>
              <input
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="29.99"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Max Pages per Audit</label>
              <input
                type="number"
                value={formData.max_pages_per_audit}
                onChange={(e) => setFormData({ ...formData, max_pages_per_audit: e.target.value })}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="10"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Max Audits per Month</label>
            <select
              value={formData.max_audits_per_month === 999999 ? 'unlimited' : formData.max_audits_per_month}
              onChange={(e) => setFormData({ ...formData, max_audits_per_month: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="1">1 audit</option>
              <option value="5">5 audits</option>
              <option value="10">10 audits</option>
              <option value="25">25 audits</option>
              <option value="50">50 audits</option>
              <option value="100">100 audits</option>
              <option value="unlimited">Unlimited</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Stripe Price ID</label>
            <input
              type="text"
              value={formData.stripe_price_id}
              onChange={(e) => setFormData({ ...formData, stripe_price_id: e.target.value })}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              placeholder="price_1234567890abcdef"
            />
            <p className="text-xs text-gray-500 mt-1">
              The Stripe Price ID for this plan. Leave empty if not using Stripe.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 text-purple-600 bg-slate-800 border-slate-700 rounded focus:ring-purple-500"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-300">
              Plan is active and available for subscription
            </label>
          </div>
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-semibold transition-colors"
            >
              Update Plan
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminDashboard;
