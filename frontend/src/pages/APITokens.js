import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from '@/api/axios';
import { Key, Plus, Trash2, Copy, Check, ArrowLeft, Eye, EyeOff } from 'lucide-react';

const APITokens = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [tokenName, setTokenName] = useState('');
  const [newToken, setNewToken] = useState(null);
  const [copiedToken, setCopiedToken] = useState(null);
  const [visibleTokens, setVisibleTokens] = useState({});

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      const response = await axios.get('/api-tokens');
      setTokens(response.data);
    } catch (error) {
      console.error('Failed to fetch tokens:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateToken = async () => {
    if (!tokenName.trim()) {
      alert('Please enter a token name');
      return;
    }

    try {
      const response = await axios.post('/api-tokens', { name: tokenName });
      setNewToken(response.data.token);
      setTokenName('');
      fetchTokens();
    } catch (error) {
      console.error('Failed to create token:', error);
      alert('Failed to create token');
    }
  };

  const handleDeleteToken = async (tokenId) => {
    if (!window.confirm('Are you sure you want to delete this token? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete(`/api-tokens/${tokenId}`);
      fetchTokens();
    } catch (error) {
      console.error('Failed to delete token:', error);
      alert('Failed to delete token');
    }
  };

  const handleToggleToken = async (tokenId, currentStatus) => {
    try {
      await axios.post(`/api-tokens/${tokenId}/toggle`);
      fetchTokens();
    } catch (error) {
      console.error('Failed to toggle token:', error);
    }
  };

  const handleCopyToken = (token) => {
    navigator.clipboard.writeText(token);
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  };

  const toggleTokenVisibility = (tokenId) => {
    setVisibleTokens(prev => ({
      ...prev,
      [tokenId]: !prev[tokenId]
    }));
  };

  const maskToken = (token) => {
    return token.substring(0, 8) + '•'.repeat(20) + token.substring(token.length - 8);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
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
              <div>
                <h1 className="text-3xl font-bold text-white">API Tokens</h1>
                <p className="text-gray-400 mt-1">Manage your API tokens for programmatic access</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg hover:shadow-purple-500/50 transition-all"
            >
              <Plus className="w-5 h-5" />
              Create Token
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Info Banner */}
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mb-8">
            <div className="flex items-start gap-4">
              <Key className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-white font-semibold mb-2">About API Tokens</h3>
                <p className="text-gray-300 text-sm mb-2">
                  API tokens allow you to access MJ SEO APIs programmatically. Use these tokens in your applications or MCP server integrations.
                </p>
                <p className="text-gray-400 text-sm">
                  Keep your tokens secure and never share them publicly. You can disable or delete tokens at any time.
                </p>
              </div>
            </div>
          </div>

          {/* Tokens List */}
          {tokens.length === 0 ? (
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-12 border border-slate-800 text-center">
              <Key className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No API Tokens Yet</h3>
              <p className="text-gray-400 mb-6">Create your first API token to get started</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                Create Token
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {tokens.map((token) => (
                <div
                  key={token.id}
                  className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-white">{token.name || 'Unnamed Token'}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          token.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}>
                          {token.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <code className="text-sm text-gray-400 bg-slate-800 px-3 py-1 rounded font-mono">
                          {visibleTokens[token.id] ? token.token : maskToken(token.token)}
                        </code>
                        <button
                          onClick={() => toggleTokenVisibility(token.id)}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {visibleTokens[token.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => handleCopyToken(token.token)}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          {copiedToken === token.token ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                      <div className="text-sm text-gray-500">
                        Created: {new Date(token.created_at).toLocaleString()}
                        {token.last_used_at && (
                          <span className="ml-4">
                            Last used: {new Date(token.last_used_at).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleToggleToken(token.id, token.is_active)}
                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                          token.is_active
                            ? 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'
                            : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                        }`}
                      >
                        {token.is_active ? 'Disable' : 'Enable'}
                      </button>
                      <button
                        onClick={() => handleDeleteToken(token.id)}
                        className="text-red-400 hover:text-red-300 transition-colors p-2"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Token Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 rounded-2xl p-8 max-w-md w-full border border-slate-800">
            <h2 className="text-2xl font-bold text-white mb-6">Create API Token</h2>
            
            {newToken ? (
              <div>
                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4 mb-4">
                  <p className="text-green-400 text-sm mb-2 font-semibold">Token created successfully!</p>
                  <p className="text-gray-300 text-sm mb-3">
                    Make sure to copy your token now. You won't be able to see it again!
                  </p>
                  <div className="bg-slate-800 p-3 rounded-lg">
                    <code className="text-sm text-white break-all">{newToken}</code>
                  </div>
                </div>
                <button
                  onClick={() => handleCopyToken(newToken)}
                  className="w-full bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-lg font-semibold transition-colors mb-3"
                >
                  {copiedToken === newToken ? (
                    <span className="flex items-center justify-center gap-2">
                      <Check className="w-5 h-5" /> Copied!
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      <Copy className="w-5 h-5" /> Copy Token
                    </span>
                  )}
                </button>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewToken(null);
                  }}
                  className="w-full bg-slate-800 hover:bg-slate-700 text-white py-3 rounded-lg font-semibold transition-colors"
                >
                  Close
                </button>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-gray-300 mb-2">
                    Token Name
                  </label>
                  <input
                    type="text"
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    placeholder="e.g., Production API, MCP Server"
                    className="w-full bg-slate-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleCreateToken}
                    className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-lg font-semibold transition-colors"
                  >
                    Create
                  </button>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      setTokenName('');
                    }}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 text-white py-3 rounded-lg font-semibold transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default APITokens;