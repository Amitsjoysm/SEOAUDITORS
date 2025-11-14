import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from '@/api/axios';
import { Check, Sparkles, Zap, Crown, ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from 'react-hot-toast';

const Plans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingPlanId, setProcessingPlanId] = useState(null);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
    if (user) {
      fetchCurrentSubscription();
    }
  }, [user]);

  const fetchPlans = async () => {
    try {
      const response = await axios.get('/plans/');
      setPlans(response.data);
    } catch (error) {
      console.error('Failed to fetch plans:', error);
      toast.error('Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await axios.get('/payments/subscription');
      setCurrentSubscription(response.data);
    } catch (error) {
      console.log('No active subscription');
    }
  };

  const handleSubscribe = async (planId, planPrice) => {
    if (!user) {
      navigate('/login', { state: { from: '/plans' } });
      return;
    }

    setProcessingPlanId(planId);

    try {
      if (planPrice === 0) {
        const response = await axios.post('/payments/create-checkout-session', {
          plan_id: planId
        });
        
        if (response.data.status === 'success') {
          toast.success('Free plan activated!');
          navigate('/dashboard');
        }
        return;
      }

      const response = await axios.post('/payments/create-checkout-session', {
        plan_id: planId
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      const message = error.response?.data?.detail || 'Failed to start checkout process';
      toast.error(message);
      setProcessingPlanId(null);
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

  const isCurrentPlan = (planId) => {
    return currentSubscription?.plan?.id === planId;
  };

  const getButtonText = (plan) => {
    if (processingPlanId === plan.id) {
      return <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Processing...</>;
    }
    
    if (isCurrentPlan(plan.id)) {
      return 'Current Plan';
    }

    if (plan.price === 0) {
      return 'Get Started Free';
    }

    if (currentSubscription && currentSubscription.plan.price < plan.price) {
      return 'Upgrade';
    }

    if (currentSubscription && currentSubscription.plan.price > plan.price) {
      return 'Downgrade';
    }

    return 'Subscribe Now';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl flex items-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin" />
          Loading plans...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
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
            Get comprehensive SEO audits with AI-powered insights powered by Stripe
          </p>

          {currentSubscription && (
            <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-blue-500/20 border border-blue-500/30 rounded-lg text-blue-300">
              <Check className="w-5 h-5" />
              Current Plan: {currentSubscription.plan.display_name}
            </div>
          )}
        </div>

        <div className="flex justify-center mb-12">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/5 border border-white/10 rounded-full">
            <svg className="w-6 h-6" viewBox="0 0 60 25" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M59.64 14.28h-8.06c.19 1.93 1.6 2.55 3.2 2.55 1.64 0 2.96-.37 4.05-.95v3.32a8.33 8.33 0 0 1-4.56 1.1c-4.01 0-6.83-2.5-6.83-7.48 0-4.19 2.39-7.52 6.3-7.52 3.92 0 5.96 3.28 5.96 7.5 0 .4-.04 1.26-.06 1.48zm-5.92-5.62c-1.03 0-2.17.73-2.17 2.58h4.25c0-1.85-1.07-2.58-2.08-2.58zM40.95 20.3c-1.44 0-2.32-.6-2.9-1.04l-.02 4.63-4.12.87V5.57h3.76l.08 1.02a4.7 4.7 0 0 1 3.23-1.29c2.9 0 5.62 2.6 5.62 7.4 0 5.23-2.7 7.6-5.65 7.6zM40 8.95c-.95 0-1.54.34-1.97.81l.02 6.12c.4.44.98.78 1.95.78 1.52 0 2.54-1.65 2.54-3.87 0-2.15-1.04-3.84-2.54-3.84zM28.24 5.57h4.13v14.44h-4.13V5.57zm0-4.7L32.37 0v3.36l-4.13.88V.88zm-4.32 9.35v9.79H19.8V5.57h3.7l.12 1.22c1-1.77 3.07-1.41 3.62-1.22v3.79c-.52-.17-2.29-.43-3.32.86zm-8.55 4.72c0 2.43 2.6 1.68 3.12 1.46v3.36c-.55.3-1.54.54-2.89.54a4.15 4.15 0 0 1-4.27-4.24l.01-13.17 4.02-.86v3.54h3.14V9.1h-3.13v5.85zm-4.91.7c0 2.97-2.31 4.66-5.73 4.66a11.2 11.2 0 0 1-4.46-.93v-3.93c1.38.75 3.1 1.31 4.46 1.31.92 0 1.53-.24 1.53-1C6.26 13.77 0 14.51 0 9.95 0 7.04 2.28 5.3 5.62 5.3c1.36 0 2.72.2 4.09.75v3.88a9.23 9.23 0 0 0-4.1-1.06c-.86 0-1.44.25-1.44.9 0 1.85 6.29.97 6.29 5.88z" fill="#fff"/>
            </svg>
            <span className="text-sm text-gray-300 font-medium">Secure payments powered by Stripe</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`relative bg-gradient-to-br ${getPlanColor(plan.name)} p-1 rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-300 hover:scale-105 ${
                isCurrentPlan(plan.id) ? 'ring-4 ring-green-400' : ''
              }`}
            >
              {plan.name.toLowerCase() === 'pro' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-yellow-400 to-orange-400 text-xs font-bold uppercase rounded-full shadow-lg z-10">
                  Most Popular
                </div>
              )}

              <div className="bg-slate-900 rounded-2xl p-6 h-full flex flex-col">
                <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${getPlanColor(plan.name)} flex items-center justify-center text-white mb-4`}>
                  {getPlanIcon(plan.name)}
                </div>

                <h3 className="text-2xl font-bold text-white mb-2">{plan.display_name}</h3>
                <p className="text-gray-400 text-sm mb-4">{plan.description}</p>

                <div className="mb-6">
                  <div className="flex items-baseline">
                    <span className="text-5xl font-bold text-white">${plan.price}</span>
                    <span className="text-gray-400 ml-2">{plan.price === 0 ? 'forever' : '/month'}</span>
                  </div>
                </div>

                <div className="flex-1 mb-6">
                  <ul className="space-y-3">
                    {plan.features && plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-gray-300">
                        <Check className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleSubscribe(plan.id, plan.price)}
                  disabled={processingPlanId === plan.id || isCurrentPlan(plan.id)}
                  className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center ${
                    isCurrentPlan(plan.id)
                      ? 'bg-green-600 text-white cursor-default'
                      : processingPlanId === plan.id
                      ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                      : `bg-gradient-to-r ${getPlanColor(plan.name)} hover:shadow-xl hover:shadow-purple-500/50 text-white`
                  }`}
                >
                  {getButtonText(plan)}
                </button>

                {plan.price > 0 && (
                  <p className="text-xs text-gray-500 text-center mt-3">
                    Cancel anytime • Secure checkout
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Plans;
