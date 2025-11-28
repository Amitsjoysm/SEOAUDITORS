import React from 'react';
import { useNavigate } from 'react-router-dom';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  CheckCircle2, Zap, Shield, TrendingUp, BarChart3, Globe, 
  Search, FileText, MessageSquare, Key, Users, Lock,
  ArrowRight, Sparkles, Clock, Award
} from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "132 Comprehensive Checks",
      description: "Deep analysis across 9 categories including Technical SEO, Performance, Content Quality, and more."
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "AI-Powered Insights",
      description: "Get actionable recommendations powered by advanced AI to boost your rankings immediately."
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Real-Time Crawling",
      description: "Automated crawler analyzes up to 20 pages in real-time with detailed performance metrics."
    },
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: "Ranking Impact Analysis",
      description: "Understand exactly how each issue affects your rankings with percentage impact scores."
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Enterprise Security",
      description: "Built with enterprise-grade security, scalability to handle 10k+ users, and 99.9% uptime."
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Detailed Reports",
      description: "Download comprehensive PDF and DOCX reports with pros, cons, solutions, and enhancements."
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "AI SEO Consultant",
      description: "Chat with our AI expert for personalized SEO advice and implementation guidance."
    },
    {
      icon: <Key className="w-6 h-6" />,
      title: "API Access",
      description: "Integrate our SEO engine into your applications with our powerful REST API."
    }
  ];

  const plans = [
    {
      name: "Free",
      price: "$0",
      period: "/month",
      description: "Perfect for trying out",
      features: [
        "2 audits per month",
        "10 pages per audit",
        "Basic SEO checks",
        "PDF reports",
        "Email support"
      ],
      cta: "Start Free",
      popular: false
    },
    {
      name: "Basic",
      price: "$29",
      period: "/month",
      description: "For small businesses",
      features: [
        "10 audits per month",
        "15 pages per audit",
        "All 132 checks",
        "PDF & DOCX reports",
        "Priority email support",
        "Chat with AI expert"
      ],
      cta: "Get Started",
      popular: true
    },
    {
      name: "Pro",
      price: "$99",
      period: "/month",
      description: "For growing companies",
      features: [
        "50 audits per month",
        "20 pages per audit",
        "All features",
        "AI insights & analysis",
        "Priority support",
        "API access",
        "Custom integrations"
      ],
      cta: "Get Started",
      popular: false
    },
    {
      name: "Enterprise",
      price: "$299",
      period: "/month",
      description: "For large organizations",
      features: [
        "Unlimited audits",
        "20 pages per audit",
        "All Pro features",
        "Dedicated support",
        "White-label reports",
        "Custom SLA",
        "Advanced API limits"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  const stats = [
    { value: "10,000+", label: "SEO Audits" },
    { value: "132+", label: "Checks" },
    { value: "99.9%", label: "Uptime" },
    { value: "24/7", label: "Support" }
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)' }}>
      <ApolloNavbar />

      {/* Hero Section */}
      <section style={{ padding: '5rem 0', background: 'white' }}>
        <div className="apollo-container">
          <div style={{ maxWidth: '900px', margin: '0 auto', textAlign: 'center' }}>
            <div style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '0.5rem',
              padding: '0.5rem 1rem',
              background: 'var(--apollo-info-light)',
              borderRadius: '9999px',
              marginBottom: '1.5rem',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: 'var(--apollo-info)'
            }}>
              <Sparkles className="w-4 h-4" />
              AI-Powered SEO Analysis Platform
            </div>

            <h1 style={{ 
              fontSize: '3.5rem', 
              fontWeight: 700, 
              lineHeight: 1.1, 
              marginBottom: '1.5rem',
              color: 'var(--apollo-gray-900)'
            }}>
              Dominate Search Rankings with{' '}
              <span style={{ 
                background: 'linear-gradient(135deg, var(--apollo-primary) 0%, var(--apollo-secondary) 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                AI-Powered SEO
              </span>
            </h1>
            
            <p style={{ 
              fontSize: '1.25rem', 
              color: 'var(--apollo-gray-600)', 
              marginBottom: '2.5rem',
              lineHeight: 1.6
            }}>
              Get comprehensive SEO analysis in minutes. 132 checks across 9 categories.
              Real-time crawling, actionable AI insights, and production-ready platform.
            </p>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button 
                size="lg" 
                onClick={() => navigate('/register')}
                style={{
                  background: 'var(--apollo-primary)',
                  color: 'white',
                  padding: '0.875rem 2rem',
                  fontSize: '1rem',
                  fontWeight: 600,
                  borderRadius: 'var(--apollo-radius)',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
                data-testid="hero-get-started-btn"
              >
                Start Free Audit
                <ArrowRight className="w-5 h-5" />
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                onClick={() => navigate('/login')}
                style={{
                  background: 'white',
                  color: 'var(--apollo-gray-700)',
                  padding: '0.875rem 2rem',
                  fontSize: '1rem',
                  fontWeight: 600,
                  borderRadius: 'var(--apollo-radius)',
                  border: '1px solid var(--apollo-gray-300)',
                  cursor: 'pointer'
                }}
              >
                View Demo
              </Button>
            </div>

            {/* Stats */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
              gap: '2rem',
              marginTop: '4rem',
              padding: '2rem',
              background: 'var(--apollo-gray-50)',
              borderRadius: 'var(--apollo-radius-lg)'
            }}>
              {stats.map((stat, index) => (
                <div key={index} style={{ textAlign: 'center' }}>
                  <div style={{ 
                    fontSize: '2rem', 
                    fontWeight: 700, 
                    color: 'var(--apollo-primary)',
                    marginBottom: '0.25rem'
                  }}>
                    {stat.value}
                  </div>
                  <div style={{ 
                    fontSize: '0.875rem', 
                    color: 'var(--apollo-gray-600)',
                    fontWeight: 500
                  }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '5rem 0' }}>
        <div className="apollo-container">
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: 700, 
              marginBottom: '1rem',
              color: 'var(--apollo-gray-900)'
            }}>
              Everything You Need for{' '}
              <span style={{ color: 'var(--apollo-primary)' }}>SEO Success</span>
            </h2>
            <p style={{ 
              fontSize: '1.125rem', 
              color: 'var(--apollo-gray-600)',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Comprehensive tools and insights to improve your search rankings and drive organic traffic
            </p>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem'
          }}>
            {features.map((feature, index) => (
              <div 
                key={index} 
                className="apollo-card"
                style={{ padding: '1.5rem', transition: 'all 0.2s ease' }}
              >
                <div style={{ 
                  display: 'inline-flex',
                  padding: '0.75rem',
                  background: 'var(--apollo-info-light)',
                  borderRadius: 'var(--apollo-radius)',
                  color: 'var(--apollo-primary)',
                  marginBottom: '1rem'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{ 
                  fontSize: '1.125rem', 
                  fontWeight: 600, 
                  marginBottom: '0.5rem',
                  color: 'var(--apollo-gray-900)'
                }}>
                  {feature.title}
                </h3>
                <p style={{ 
                  fontSize: '0.875rem', 
                  color: 'var(--apollo-gray-600)',
                  lineHeight: 1.6
                }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section style={{ padding: '5rem 0', background: 'white' }}>
        <div className="apollo-container">
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: 700, 
              marginBottom: '1rem',
              color: 'var(--apollo-gray-900)'
            }}>
              Simple, Transparent{' '}
              <span style={{ color: 'var(--apollo-primary)' }}>Pricing</span>
            </h2>
            <p style={{ 
              fontSize: '1.125rem', 
              color: 'var(--apollo-gray-600)'
            }}>
              Choose the perfect plan for your SEO needs
            </p>
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1.5rem',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            {plans.map((plan, index) => (
              <div 
                key={index}
                className="apollo-card"
                style={{ 
                  padding: '2rem',
                  position: 'relative',
                  border: plan.popular ? '2px solid var(--apollo-primary)' : '1px solid var(--apollo-gray-200)',
                  boxShadow: plan.popular ? 'var(--apollo-shadow-lg)' : 'var(--apollo-shadow)'
                }}
              >
                {plan.popular && (
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
                    Most Popular
                  </div>
                )}

                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ 
                    fontSize: '1.5rem', 
                    fontWeight: 700,
                    marginBottom: '0.5rem',
                    color: 'var(--apollo-gray-900)'
                  }}>
                    {plan.name}
                  </h3>
                  <p style={{ 
                    fontSize: '0.875rem', 
                    color: 'var(--apollo-gray-600)'
                  }}>
                    {plan.description}
                  </p>
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <span style={{ 
                    fontSize: '3rem', 
                    fontWeight: 700,
                    color: 'var(--apollo-gray-900)'
                  }}>
                    {plan.price}
                  </span>
                  <span style={{ 
                    fontSize: '1rem', 
                    color: 'var(--apollo-gray-600)'
                  }}>
                    {plan.period}
                  </span>
                </div>

                <Button
                  onClick={() => navigate('/register')}
                  style={{
                    width: '100%',
                    background: plan.popular ? 'var(--apollo-primary)' : 'white',
                    color: plan.popular ? 'white' : 'var(--apollo-gray-700)',
                    border: plan.popular ? 'none' : '1px solid var(--apollo-gray-300)',
                    padding: '0.75rem',
                    borderRadius: 'var(--apollo-radius)',
                    fontWeight: 600,
                    cursor: 'pointer',
                    marginBottom: '1.5rem'
                  }}
                >
                  {plan.cta}
                </Button>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {plan.features.map((feature, i) => (
                    <li 
                      key={i} 
                      style={{ 
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.75rem',
                        marginBottom: '0.75rem',
                        fontSize: '0.875rem',
                        color: 'var(--apollo-gray-700)'
                      }}
                    >
                      <CheckCircle2 
                        className="w-5 h-5" 
                        style={{ 
                          color: 'var(--apollo-success)',
                          flexShrink: 0,
                          marginTop: '2px'
                        }} 
                      />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section style={{ padding: '5rem 0' }}>
        <div className="apollo-container">
          <div className="apollo-card" style={{ 
            padding: '4rem 2rem',
            background: 'linear-gradient(135deg, var(--apollo-primary) 0%, var(--apollo-secondary) 100%)',
            border: 'none',
            textAlign: 'center'
          }}>
            <h2 style={{ 
              fontSize: '2.5rem', 
              fontWeight: 700, 
              color: 'white',
              marginBottom: '1rem'
            }}>
              Ready to Boost Your Rankings?
            </h2>
            <p style={{ 
              fontSize: '1.125rem', 
              color: 'rgba(255, 255, 255, 0.9)',
              marginBottom: '2rem',
              maxWidth: '600px',
              margin: '0 auto 2rem'
            }}>
              Join thousands of businesses using MJ SEO to improve their search visibility
            </p>
            <Button
              size="lg"
              onClick={() => navigate('/register')}
              style={{
                background: 'white',
                color: 'var(--apollo-primary)',
                padding: '0.875rem 2rem',
                fontSize: '1rem',
                fontWeight: 600,
                borderRadius: 'var(--apollo-radius)',
                border: 'none',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </section>

      <ApolloFooter />
    </div>
  );
};

export default Landing;
