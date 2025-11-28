import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from '@/api/axios';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Loader2, Sparkles, Zap, Crown, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Plans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingPlanId, setProcessingPlanId] = useState(null);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const { user } = useAuth();
  const { toast } = useToast();
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
      toast({
        title: "Error",
        description: "Failed to load plans",
        variant: "destructive"
      });
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
          toast({
            title: "Success!",
            description: "Free plan activated!"
          });
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
      toast({
        title: "Error",
        description: message,
        variant: "destructive"
      });
      setProcessingPlanId(null);
    }
  };

  const getPlanIcon = (planName) => {
    const icons = {
      'free': <Sparkles className="w-6 h-6" />,
      'basic': <Zap className="w-6 h-6" />,
      'pro': <Crown className="w-6 h-6" />,
      'enterprise': <Crown className="w-6 h-6" />
    };
    return icons[planName.toLowerCase()] || <Check className="w-6 h-6" />;
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

    return 'Subscribe Now';
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--apollo-gray-700)' }}>
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Loading plans...</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />

      <div className="apollo-container" style={{ padding: '4rem 1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ 
            fontSize: '3rem', 
            fontWeight: 700, 
            color: 'var(--apollo-gray-900)', 
            marginBottom: '1rem' 
          }}>
            Choose Your{' '}
            <span style={{ 
              background: 'linear-gradient(135deg, var(--apollo-primary) 0%, var(--apollo-secondary) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Plan
            </span>
          </h1>
          <p style={{ fontSize: '1.125rem', color: 'var(--apollo-gray-600)', maxWidth: '600px', margin: '0 auto' }}>
            Get comprehensive SEO audits with AI-powered insights
          </p>

          {currentSubscription && (
            <div style={{ 
              marginTop: '1.5rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.5rem',
              background: 'var(--apollo-success-light)',
              border: '1px solid var(--apollo-success)',
              borderRadius: 'var(--apollo-radius-lg)',
              color: 'var(--apollo-success)',
              fontWeight: 500
            }}>
              <CheckCircle2 className="w-5 h-5" />
              Current Plan: {currentSubscription.plan.display_name}
            </div>
          )}
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          {plans.map((plan) => {
            const isPopular = plan.name.toLowerCase() === 'basic' || plan.name.toLowerCase() === 'pro';
            const isCurrent = isCurrentPlan(plan.id);
            
            return (
              <div
                key={plan.id}
                className="apollo-card"
                style={{ 
                  padding: '2rem',
                  position: 'relative',
                  border: isPopular ? '2px solid var(--apollo-primary)' : '1px solid var(--apollo-gray-200)',
                  boxShadow: isPopular ? 'var(--apollo-shadow-lg)' : 'var(--apollo-shadow)'
                }}
              >
                {isPopular && (
                  <div style={{
                    position: 'absolute',
                    top: '-12px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'var(--apollo-primary)',
                    color: 'white',
                    padding: '0.25rem 1rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    Popular
                  </div>
                )}

                <div style={{ 
                  display: 'inline-flex',
                  padding: '0.75rem',
                  background: 'var(--apollo-info-light)',
                  borderRadius: 'var(--apollo-radius)',
                  color: 'var(--apollo-primary)',
                  marginBottom: '1rem'
                }}>
                  {getPlanIcon(plan.name)}
                </div>

                <h3 style={{ 
                  fontSize: '1.5rem', 
                  fontWeight: 700,
                  marginBottom: '0.5rem',
                  color: 'var(--apollo-gray-900)'
                }}>
                  {plan.display_name}
                </h3>
                
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: 'var(--apollo-gray-600)',
                  marginBottom: '1.5rem'
                }}>
                  {plan.description}
                </p>

                <div style={{ marginBottom: '1.5rem' }}>
                  <span style={{ 
                    fontSize: '3rem', 
                    fontWeight: 700,
                    color: 'var(--apollo-gray-900)'
                  }}>
                    ${plan.price}
                  </span>
                  <span style={{ 
                    fontSize: '1rem', 
                    color: 'var(--apollo-gray-600)'
                  }}>
                    /month
                  </span>
                </div>

                <Button
                  onClick={() => handleSubscribe(plan.id, plan.price)}
                  disabled={processingPlanId === plan.id || isCurrent}
                  className={isCurrent ? "apollo-btn apollo-btn-secondary" : "apollo-btn apollo-btn-primary"}
                  style={{ 
                    width: '100%',
                    marginBottom: '1.5rem',
                    opacity: isCurrent ? 0.7 : 1
                  }}
                >
                  {getButtonText(plan)}
                </Button>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  <li style={{ 
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    marginBottom: '0.75rem',
                    fontSize: '0.875rem',
                    color: 'var(--apollo-gray-700)'
                  }}>
                    <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                    <span>{plan.max_audits_per_month} audits per month</span>
                  </li>
                  <li style={{ 
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    marginBottom: '0.75rem',
                    fontSize: '0.875rem',
                    color: 'var(--apollo-gray-700)'
                  }}>
                    <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                    <span>{plan.max_pages_per_audit} pages per audit</span>
                  </li>
                  <li style={{ 
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    marginBottom: '0.75rem',
                    fontSize: '0.875rem',
                    color: 'var(--apollo-gray-700)'
                  }}>
                    <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                    <span>All 132 SEO checks</span>
                  </li>
                  <li style={{ 
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.75rem',
                    marginBottom: '0.75rem',
                    fontSize: '0.875rem',
                    color: 'var(--apollo-gray-700)'
                  }}>
                    <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                    <span>PDF & DOCX reports</span>
                  </li>
                  {plan.price > 0 && (
                    <li style={{ 
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      marginBottom: '0.75rem',
                      fontSize: '0.875rem',
                      color: 'var(--apollo-gray-700)'
                    }}>
                      <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                      <span>Priority support</span>
                    </li>
                  )}
                  {(plan.name.toLowerCase() === 'pro' || plan.name.toLowerCase() === 'enterprise') && (
                    <>
                      <li style={{ 
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.75rem',
                        marginBottom: '0.75rem',
                        fontSize: '0.875rem',
                        color: 'var(--apollo-gray-700)'
                      }}>
                        <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                        <span>API access</span>
                      </li>
                      <li style={{ 
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.75rem',
                        fontSize: '0.875rem',
                        color: 'var(--apollo-gray-700)'
                      }}>
                        <CheckCircle2 className="w-5 h-5" style={{ color: 'var(--apollo-success)', flexShrink: 0, marginTop: '2px' }} />
                        <span>AI chat consultant</span>
                      </li>
                    </>
                  )}
                </ul>
              </div>
            );
          })}
        </div>
      </div>

      <ApolloFooter />
    </div>
  );
};

export default Plans;
