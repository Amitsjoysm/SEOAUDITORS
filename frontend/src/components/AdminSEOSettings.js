import React, { useState, useEffect } from 'react';
import axios from '@/api/axios';
import { Save, Loader, Check, X, Globe } from 'lucide-react';

const AdminSEOSettings = () => {
  const [seoSettings, setSeoSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchSEOSettings();
  }, []);

  const fetchSEOSettings = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/admin/seo-settings/');
      setSeoSettings(response.data);
      setFormData(response.data);
    } catch (error) {
      console.error('Failed to fetch SEO settings:', error);
      setError(error.response?.data?.detail || 'Failed to load SEO settings');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccessMessage('');
    
    try {
      if (seoSettings?.id) {
        await axios.put(`/admin/seo-settings/${seoSettings.id}`, formData);
      } else {
        await axios.post('/admin/seo-settings/', formData);
      }
      setSuccessMessage('SEO settings saved successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      await fetchSEOSettings();
    } catch (error) {
      console.error('Failed to save SEO settings:', error);
      setError(error.response?.data?.detail || 'Failed to save SEO settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className=\"flex items-center justify-center p-12\">
        <Loader className=\"animate-spin w-8 h-8 text-purple-500\" />
      </div>
    );
  }

  return (
    <div className=\"space-y-6\">
      {/* Header */}
      <div className=\"flex items-center justify-between\">
        <div>
          <h2 className=\"text-2xl font-bold text-white mb-2\">SEO Settings</h2>
          <p className=\"text-slate-400\">Manage meta tags, Open Graph, and analytics for your application</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className=\"flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50\"
        >
          {saving ? (
            <>
              <Loader className=\"w-4 h-4 animate-spin\" />
              Saving...
            </>
          ) : (
            <>
              <Save className=\"w-4 h-4\" />
              Save Settings
            </>
          )}
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className=\"p-4 bg-red-900/20 border border-red-500 rounded-lg flex items-center gap-2 text-red-300\">
          <X className=\"w-5 h-5\" />
          {error}
        </div>
      )}

      {successMessage && (
        <div className=\"p-4 bg-green-900/20 border border-green-500 rounded-lg flex items-center gap-2 text-green-300\">
          <Check className=\"w-5 h-5\" />
          {successMessage}
        </div>
      )}

      {/* Meta Tags Section */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4 flex items-center gap-2\">
          <Globe className=\"w-5 h-5 text-purple-400\" />
          Basic Meta Tags
        </h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Site Title</label>
            <input
              type=\"text\"
              value={formData.site_title || ''}
              onChange={(e) => handleChange('site_title', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"MJ SEO - AI-Powered SEO Audit Platform\"
            />
          </div>
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Site Description</label>
            <textarea
              value={formData.site_description || ''}
              onChange={(e) => handleChange('site_description', e.target.value)}
              rows={3}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"Production-ready SEO audit platform with comprehensive checks\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Keywords (comma-separated)</label>
            <input
              type=\"text\"
              value={formData.site_keywords || ''}
              onChange={(e) => handleChange('site_keywords', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"SEO audit, SEO tools, website analysis\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Author</label>
            <input
              type=\"text\"
              value={formData.author || ''}
              onChange={(e) => handleChange('author', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"MJ SEO Team\"
            />
          </div>
        </div>
      </div>

      {/* Open Graph Section */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4\">Open Graph (Social Media)</h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">OG Title</label>
            <input
              type=\"text\"
              value={formData.og_title || ''}
              onChange={(e) => handleChange('og_title', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">OG Description</label>
            <textarea
              value={formData.og_description || ''}
              onChange={(e) => handleChange('og_description', e.target.value)}
              rows={2}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">OG Image URL</label>
            <input
              type=\"url\"
              value={formData.og_image || ''}
              onChange={(e) => handleChange('og_image', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"https://example.com/og-image.jpg\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">OG URL</label>
            <input
              type=\"url\"
              value={formData.og_url || ''}
              onChange={(e) => handleChange('og_url', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"https://example.com\"
            />
          </div>
        </div>
      </div>

      {/* Twitter Card Section */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4\">Twitter Card</h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Twitter Card Type</label>
            <select
              value={formData.twitter_card || 'summary_large_image'}
              onChange={(e) => handleChange('twitter_card', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            >
              <option value=\"summary\">Summary</option>
              <option value=\"summary_large_image\">Summary Large Image</option>
            </select>
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Twitter Site (@username)</label>
            <input
              type=\"text\"
              value={formData.twitter_site || ''}
              onChange={(e) => handleChange('twitter_site', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"@mjseo\"
            />
          </div>
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Twitter Image URL</label>
            <input
              type=\"url\"
              value={formData.twitter_image || ''}
              onChange={(e) => handleChange('twitter_image', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
        </div>
      </div>

      {/* Analytics Section */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4\">Analytics & Tracking</h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Google Analytics 4 ID</label>
            <input
              type=\"text\"
              value={formData.google_analytics_id || ''}
              onChange={(e) => handleChange('google_analytics_id', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"G-XXXXXXXXXX\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Google Tag Manager ID</label>
            <input
              type=\"text\"
              value={formData.google_tag_manager_id || ''}
              onChange={(e) => handleChange('google_tag_manager_id', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"GTM-XXXXXXX\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Google Site Verification</label>
            <input
              type=\"text\"
              value={formData.google_site_verification || ''}
              onChange={(e) => handleChange('google_site_verification', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
              placeholder=\"Verification meta tag content\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Facebook Domain Verification</label>
            <input
              type=\"text\"
              value={formData.facebook_domain_verification || ''}
              onChange={(e) => handleChange('facebook_domain_verification', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
        </div>
      </div>

      {/* Organization Schema Section */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4\">Organization Information (Schema.org)</h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Organization Name</label>
            <input
              type=\"text\"
              value={formData.organization_name || ''}
              onChange={(e) => handleChange('organization_name', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Organization Logo URL</label>
            <input
              type=\"url\"
              value={formData.organization_logo || ''}
              onChange={(e) => handleChange('organization_logo', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div className=\"md:col-span-2\">
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Organization Description</label>
            <textarea
              value={formData.organization_description || ''}
              onChange={(e) => handleChange('organization_description', e.target.value)}
              rows={2}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Organization Email</label>
            <input
              type=\"email\"
              value={formData.organization_email || ''}
              onChange={(e) => handleChange('organization_email', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
          <div>
            <label className=\"block text-sm font-medium text-slate-300 mb-2\">Organization Phone</label>
            <input
              type=\"tel\"
              value={formData.organization_phone || ''}
              onChange={(e) => handleChange('organization_phone', e.target.value)}
              className=\"w-full px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white focus:ring-2 focus:ring-purple-500\"
            />
          </div>
        </div>
      </div>

      {/* Performance Settings */}
      <div className=\"bg-slate-800/50 rounded-lg p-6 border border-slate-700\">
        <h3 className=\"text-xl font-semibold text-white mb-4\">Performance & Optimization</h3>
        <div className=\"grid grid-cols-1 md:grid-cols-2 gap-4\">
          <label className=\"flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg border border-slate-600 cursor-pointer hover:border-purple-500 transition-colors\">
            <input
              type=\"checkbox\"
              checked={formData.enable_lazy_loading || false}
              onChange={(e) => handleChange('enable_lazy_loading', e.target.checked)}
              className=\"w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500\"
            />
            <div>
              <div className=\"text-white font-medium\">Lazy Loading</div>
              <div className=\"text-slate-400 text-sm\">Enable lazy loading for images</div>
            </div>
          </label>
          <label className=\"flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg border border-slate-600 cursor-pointer hover:border-purple-500 transition-colors\">
            <input
              type=\"checkbox\"
              checked={formData.enable_image_optimization || false}
              onChange={(e) => handleChange('enable_image_optimization', e.target.checked)}
              className=\"w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500\"
            />
            <div>
              <div className=\"text-white font-medium\">Image Optimization</div>
              <div className=\"text-slate-400 text-sm\">Optimize images for web</div>
            </div>
          </label>
          <label className=\"flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg border border-slate-600 cursor-pointer hover:border-purple-500 transition-colors\">
            <input
              type=\"checkbox\"
              checked={formData.enable_minification || false}
              onChange={(e) => handleChange('enable_minification', e.target.checked)}
              className=\"w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500\"
            />
            <div>
              <div className=\"text-white font-medium\">Code Minification</div>
              <div className=\"text-slate-400 text-sm\">Minify CSS and JavaScript</div>
            </div>
          </label>
          <label className=\"flex items-center gap-3 p-4 bg-slate-900/50 rounded-lg border border-slate-600 cursor-pointer hover:border-purple-500 transition-colors\">
            <input
              type=\"checkbox\"
              checked={formData.enable_compression || false}
              onChange={(e) => handleChange('enable_compression', e.target.checked)}
              className=\"w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-500\"
            />
            <div>
              <div className=\"text-white font-medium\">Compression</div>
              <div className=\"text-slate-400 text-sm\">Enable Gzip/Brotli compression</div>
            </div>
          </label>
        </div>
      </div>
    </div>
  );
};

export default AdminSEOSettings;
