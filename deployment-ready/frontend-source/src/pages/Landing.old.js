import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle2, Zap, Shield, TrendingUp, BarChart3, Globe } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <BarChart3 className="w-8 h-8" />,
      title: "132 Comprehensive Checks",
      description: "Deep analysis across 9 categories including Technical SEO, Performance, Content Quality, and more."
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "AI-Powered Insights",
      description: "Get actionable recommendations powered by advanced AI to boost your rankings immediately."
    },
    {
      icon: <Globe className="w-8 h-8" />,
      title: "Real-Time Crawling",
      description: "Automated crawler analyzes up to 20 pages in real-time with detailed performance metrics."
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "Ranking Impact Analysis",
      description: "Understand exactly how each issue affects your rankings with percentage impact scores."
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Production Ready",
      description: "Built with enterprise-grade security, scalability to handle 10k+ users, and 99.9% uptime."
    },
    {
      icon: <CheckCircle2 className="w-8 h-8" />,
      title: "Detailed Reports",
      description: "Download comprehensive PDF and DOCX reports with pros, cons, solutions, and enhancements."
    }
  ];

  const plans = [
    {
      name: "Free",
      price: "$0",
      features: ["2 audits/month", "10 pages per audit", "Basic checks", "PDF reports"]
    },
    {
      name: "Basic",
      price: "$29",
      popular: true,
      features: ["10 audits/month", "15 pages per audit", "All 132 checks", "PDF & DOCX reports", "Email support"]
    },
    {
      name: "Pro",
      price: "$99",
      features: ["50 audits/month", "20 pages per audit", "AI insights", "Chat with AI expert", "Priority support", "API access"]
    },
    {
      name: "Enterprise",
      price: "$299",
      features: ["Unlimited audits", "20 pages per audit", "All features", "Dedicated support", "Custom integrations", "White-label reports"]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Navbar */}
      <nav className="border-b border-white/10 backdrop-blur-sm bg-slate-950/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-8 h-8 text-blue-400" />
            <span className="text-2xl font-bold text-white">MJ SEO</span>
          </div>
          <div className="flex gap-3">
            <Button variant="ghost" className="text-white" onClick={() => navigate('/login')}>
              Login
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => navigate('/register')}>
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-white mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Dominate Search Rankings
            </span>
            <br />
            with AI-Powered SEO Audits
          </h1>
          <p className="text-xl text-slate-300 mb-10">
            Get comprehensive SEO analysis in minutes. 132 checks across 9 categories.
            <br />
            Real-time crawling. Actionable AI insights. Production-ready platform.
          </p>
          <div className="flex gap-4 justify-center">
            <Button 
              size="lg" 
              className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-6"
              onClick={() => navigate('/register')}
              data-testid="hero-get-started-btn"
            >
              Start Free Audit
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="text-white border-white/30 hover:bg-white/10 text-lg px-8 py-6"
              onClick={() => navigate('/login')}
            >
              View Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center text-white mb-16">
          Everything You Need for <span className="text-blue-400">SEO Success</span>
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="bg-slate-900/50 border-white/10 backdrop-blur-sm hover:bg-slate-900/70 transition-all duration-300 hover:scale-105">
              <CardContent className="p-6">
                <div className="text-blue-400 mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-slate-400">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center text-white mb-4">
          Simple, Transparent <span className="text-blue-400">Pricing</span>
        </h2>
        <p className="text-center text-slate-300 mb-16 text-lg">Choose the perfect plan for your SEO needs</p>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <Card 
              key={index} 
              className={`bg-slate-900/50 border-white/10 backdrop-blur-sm hover:scale-105 transition-all duration-300 ${
                plan.popular ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <CardContent className="p-6">
                {plan.popular && (
                  <div className="text-blue-400 text-sm font-semibold mb-2">MOST POPULAR</div>
                )}
                <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                <div className="text-4xl font-bold text-blue-400 mb-6">
                  {plan.price}
                  <span className="text-lg text-slate-400">/mo</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start text-slate-300">
                      <CheckCircle2 className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button 
                  className={`w-full ${
                    plan.popular 
                      ? 'bg-blue-600 hover:bg-blue-700' 
                      : 'bg-slate-800 hover:bg-slate-700'
                  }`}
                  onClick={() => navigate('/register')}
                >
                  Get Started
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 backdrop-blur-sm bg-slate-950/50 mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-slate-400">
          <p>&copy; 2024 MJ SEO. All rights reserved. Built for SEO excellence.</p>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
