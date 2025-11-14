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
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [editingTheme, setEditingTheme] = useState(null);
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [editingKey, setEditingKey] = useState(null);
  const [showKeyValue, setShowKeyValue] = useState({});

  useEffect(() => {
    if (user?.role !== 'superadmin') {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, plansRes, themesRes, auditsRes, envKeysRes] = await Promise.all([
        axios.get('/admin/stats'),
        axios.get('/admin/users'),
        axios.get('/plans'),
        axios.get('/themes'),
        axios.get('/admin/audits'),
        axios.get('/admin/env-keys')
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
      setPlans(plansRes.data);
      setThemes(themesRes.data);
      setAudits(auditsRes.data);
      setEnvKeys(envKeysRes.data);
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading admin dashboard...</div>
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
            { id: 'audits', label: 'Audits', icon: FileText }
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
              <div key={plan.id} className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
                <h3 className="text-2xl font-bold text-white mb-2">{plan.display_name}</h3>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>
                <div className="text-3xl font-bold text-white mb-4">${plan.price}/mo</div>
                <div className="space-y-2">
                  <div className="text-sm text-gray-300">
                    <strong>Max Audits:</strong> {plan.max_audits_per_month === 999999 ? 'Unlimited' : plan.max_audits_per_month}
                  </div>
                  <div className="text-sm text-gray-300">
                    <strong>Pages per Audit:</strong> {plan.max_pages_per_audit}
                  </div>
                  <div className="text-sm">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                      plan.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {plan.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
      </div>
    </div>
  );
};

export default AdminDashboard;
