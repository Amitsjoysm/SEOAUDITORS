import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from '@/api/axios';
import { Check, Sparkles, Zap, Crown, ArrowLeft } from 'lucide-react';

const Plans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('stripe');
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get('/plans');
      setPlans(response.data);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      const response = await axios.post('/payments/create-checkout-session', {
        plan_id: planId,
        payment_provider: selectedPaymentMethod
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      alert('Failed to start checkout process. Please try again.');
    }
  };

  const getPlanIcon = (planName) => {
    const icons = {
      'free': <Sparkles className="w-8 h-8" />,
      'basic': <Zap className="w-8 h-8" />,
      'pro': <Crown className="w-8 h-8" />,
      'enterprise': <Crown className="w-8 h-8" />
    };
    return icons[planName.toLowerCase()] || <Check className="w-8 h-8" />;
  };

  const getPlanColor = (planName) => {
    const colors = {
      'free': 'from-slate-600 to-slate-700',
      'basic': 'from-blue-500 to-purple-600',
      'pro': 'from-purple-500 to-pink-600',
      'enterprise': 'from-amber-500 to-orange-600'
    };
    return colors[planName.toLowerCase()] || 'from-gray-600 to-gray-700';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading plans...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Header */}
      <div className="container mx-auto px-4 py-8">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Home
        </button>

        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Choose Your <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Plan</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Get comprehensive SEO audits with AI-powered insights
          </p>
        </div>

        {/* Payment Method Selector */}
        <div className="flex justify-center gap-4 mb-12">
          <button
            onClick={() => setSelectedPaymentMethod('stripe')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              selectedPaymentMethod === 'stripe'
                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/50'
                : 'bg-slate-800 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Stripe
          </button>
          <button
            onClick={() => setSelectedPaymentMethod('razorpay')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              selectedPaymentMethod === 'razorpay'
                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/50'
                : 'bg-slate-800 text-gray-400 hover:bg-slate-700'
            }`}
          >
            Razorpay
          </button>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-slate-900/50 backdrop-blur-xl rounded-2xl p-8 border border-slate-800 hover:border-purple-500/50 transition-all duration-300 ${
                plan.name === 'pro' ? 'transform lg:scale-105 shadow-2xl shadow-purple-500/20' : ''
              }`}
            >
              {plan.name === 'pro' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
              )}

              <div className={`bg-gradient-to-br ${getPlanColor(plan.name)} w-16 h-16 rounded-xl flex items-center justify-center text-white mb-6`}>
                {getPlanIcon(plan.name)}
              </div>

              <h3 className="text-2xl font-bold text-white mb-2">{plan.display_name}</h3>
              <p className="text-gray-400 text-sm mb-6">{plan.description}</p>

              <div className="mb-6">
                <span className="text-5xl font-bold text-white">${plan.price}</span>
                <span className="text-gray-400">/month</span>
              </div>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={plan.price === 0 && user}
                className={`w-full py-3 rounded-lg font-semibold transition-all mb-8 ${
                  plan.name === 'pro'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:shadow-lg hover:shadow-purple-500/50'
                    : 'bg-slate-800 text-white hover:bg-slate-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {plan.price === 0 ? 'Get Started' : 'Subscribe Now'}
              </button>

              <div className="space-y-4">
                <div className="text-sm font-semibold text-gray-300 mb-3">Features:</div>
                {plan.features && plan.features.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-20 max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            All plans include
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-400 text-sm">Get intelligent insights powered by advanced AI</p>
            </div>
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
                <Check className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">132+ SEO Checks</h3>
              <p className="text-gray-400 text-sm">Comprehensive analysis of all SEO factors</p>
            </div>
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl p-6 border border-slate-800">
              <div className="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-pink-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Detailed Reports</h3>
              <p className="text-gray-400 text-sm">Download PDF and DOCX reports</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Plans;
