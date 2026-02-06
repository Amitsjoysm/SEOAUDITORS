import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import axios from '@/api/axios';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';

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
      <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4" style={{ color: 'var(--apollo-primary)' }} />
          <p style={{ color: 'var(--apollo-gray-700)', fontSize: '1.125rem' }}>Processing your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />
      
      <div className="apollo-container" style={{ padding: '4rem 1.5rem' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          {/* Success Animation */}
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <div style={{ 
              display: 'inline-block', 
              padding: '1.5rem', 
              background: 'var(--apollo-success-light)', 
              borderRadius: '50%', 
              marginBottom: '1.5rem'
            }}>
              <CheckCircle className="w-20 h-20" style={{ color: 'var(--apollo-success)' }} />
            </div>
            <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--apollo-gray-900)', marginBottom: '0.5rem' }}>
              Payment Successful!
            </h1>
            <p style={{ color: 'var(--apollo-gray-600)', fontSize: '1.125rem' }}>
              Your subscription is now active
            </p>
          </div>

          {/* Subscription Details */}
          {subscription && (
            <div className="apollo-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--apollo-gray-900)', marginBottom: '1.5rem' }}>
                Subscription Details
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--apollo-gray-600)' }}>Plan:</span>
                  <span style={{ color: 'var(--apollo-gray-900)', fontWeight: 500 }}>{subscription.plan.display_name}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--apollo-gray-600)' }}>Price:</span>
                  <span style={{ color: 'var(--apollo-gray-900)', fontWeight: 500 }}>${subscription.plan.price}/month</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--apollo-gray-600)' }}>Audits per month:</span>
                  <span style={{ color: 'var(--apollo-gray-900)', fontWeight: 500 }}>{subscription.plan.max_audits_per_month}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--apollo-gray-600)' }}>Status:</span>
                  <span className="apollo-badge apollo-badge-success" style={{ textTransform: 'capitalize' }}>
                    {subscription.status}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* CTA Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
            <button
              onClick={() => navigate('/dashboard')}
              className="apollo-btn apollo-btn-primary"
              style={{ width: '100%', padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', fontSize: '1rem' }}
            >
              Go to Dashboard
              <ArrowRight className="w-5 h-5" />
            </button>
            
            <button
              onClick={() => navigate('/settings')}
              className="apollo-btn apollo-btn-secondary"
              style={{ width: '100%', padding: '1rem', fontSize: '1rem' }}
            >
              Manage Subscription
            </button>
          </div>

          {/* Email Confirmation Notice */}
          <p style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-500)', textAlign: 'center' }}>
            A confirmation email with your receipt has been sent to your email address
          </p>
        </div>
      </div>

      <ApolloFooter />
    </div>
  );
};

export default PaymentSuccess;
