import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import axios from '@/api/axios';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [subscription, setSubscription] = useState(null);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    // Fetch subscription details after successful payment
    const fetchSubscription = async () => {
      try {
        const response = await axios.get('/payments/subscription');
        setSubscription(response.data);
      } catch (error) {
        console.error('Error fetching subscription:', error);
      } finally {
        setLoading(false);
      }
    };

    if (sessionId) {
      // Give Stripe webhook time to process
      setTimeout(fetchSubscription, 2000);
    } else {
      setLoading(false);
    }
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-400 mx-auto mb-4" />
          <p className="text-white text-lg">Processing your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Success Animation */}
        <div className="text-center mb-8">
          <div className="inline-block p-4 bg-green-500/20 rounded-full mb-4">
            <CheckCircle className="w-20 h-20 text-green-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Payment Successful!</h1>
          <p className="text-gray-400">Your subscription is now active</p>
        </div>

        {/* Subscription Details */}
        {subscription && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Subscription Details</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Plan:</span>
                <span className="text-white font-medium">{subscription.plan.display_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Price:</span>
                <span className="text-white font-medium">${subscription.plan.price}/month</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Audits per month:</span>
                <span className="text-white font-medium">{subscription.plan.max_audits_per_month}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className="text-green-400 font-medium capitalize">{subscription.status}</span>
              </div>
            </div>
          </div>
        )}

        {/* CTA Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 px-6 rounded-xl font-semibold hover:shadow-xl hover:shadow-purple-500/50 transition-all flex items-center justify-center gap-2"
          >
            Go to Dashboard
            <ArrowRight className="w-5 h-5" />
          </button>
          
          <button
            onClick={() => navigate('/settings')}
            className="w-full bg-white/5 border border-white/10 text-white py-3 px-6 rounded-xl font-semibold hover:bg-white/10 transition-all"
          >
            Manage Subscription
          </button>
        </div>

        {/* Email Confirmation Notice */}
        <p className="text-sm text-gray-500 text-center mt-6">
          A confirmation email with your receipt has been sent to your email address
        </p>
      </div>
    </div>
  );
};

export default PaymentSuccess;
