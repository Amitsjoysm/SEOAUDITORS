import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import axios from '@/api/axios';
import ApolloNavbar from '@/components/ApolloNavbar';
import ApolloFooter from '@/components/ApolloFooter';
import { Send, ArrowLeft, Bot, User } from 'lucide-react';

const Chat = () => {
  const { auditId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [audit, setAudit] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchAuditAndMessages();
  }, [auditId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchAuditAndMessages = async () => {
    try {
      const [auditRes, messagesRes] = await Promise.all([
        axios.get(`/audits/${auditId}`),
        axios.get(`/chat/${auditId}`)
      ]);
      setAudit(auditRes.data);
      setMessages(messagesRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`/chat/`, {
        audit_id: auditId,
        content: input
      });
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--apollo-gray-50)', display: 'flex', flexDirection: 'column' }}>
      <ApolloNavbar />

      {/* Chat Container */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '1.5rem' }}>
        {/* Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <button
            onClick={() => navigate(`/audit/${auditId}`)}
            className="apollo-navbar-link"
            style={{ display: 'inline-flex', marginBottom: '1rem' }}
          >
            <ArrowLeft className="w-4 h-4" style={{ marginRight: '0.5rem' }} />
            Back to Audit
          </button>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: 'var(--apollo-gray-900)', marginBottom: '0.25rem' }}>
            SEO Consultant Chat
          </h1>
          {audit && (
            <p style={{ fontSize: '0.875rem', color: 'var(--apollo-gray-600)' }}>{audit.website_url}</p>
          )}
        </div>

        {/* Messages Area */}
        <div className="apollo-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '1.5rem', overflowY: 'auto', maxHeight: 'calc(100vh - 300px)' }}>
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--apollo-gray-500)' }}>
                <Bot className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--apollo-gray-400)' }} />
                <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem', color: 'var(--apollo-gray-700)' }}>
                  Start a conversation
                </p>
                <p style={{ fontSize: '0.875rem' }}>
                  Ask me anything about your SEO audit results
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      gap: '1rem',
                      alignItems: 'flex-start',
                      flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                    }}
                  >
                    <div
                      style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        background: msg.role === 'user' ? 'var(--apollo-primary)' : 'var(--apollo-gray-200)',
                        color: msg.role === 'user' ? 'white' : 'var(--apollo-gray-700)'
                      }}
                    >
                      {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                    </div>
                    <div
                      style={{
                        flex: 1,
                        maxWidth: '70%',
                        padding: '1rem',
                        borderRadius: 'var(--apollo-radius-lg)',
                        background: msg.role === 'user' ? 'var(--apollo-primary)' : 'var(--apollo-gray-100)',
                        color: msg.role === 'user' ? 'white' : 'var(--apollo-gray-900)'
                      }}
                    >
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--apollo-gray-200)', color: 'var(--apollo-gray-700)' }}>
                      <Bot className="w-5 h-5" />
                    </div>
                    <div style={{ padding: '1rem', borderRadius: 'var(--apollo-radius-lg)', background: 'var(--apollo-gray-100)' }}>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--apollo-gray-400)', animation: 'bounce 1.4s infinite ease-in-out' }}></div>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--apollo-gray-400)', animation: 'bounce 1.4s 0.2s infinite ease-in-out' }}></div>
                        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--apollo-gray-400)', animation: 'bounce 1.4s 0.4s infinite ease-in-out' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        <div style={{ marginTop: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-end' }}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your SEO audit..."
              disabled={loading}
              className="apollo-input"
              style={{ flex: 1, minHeight: '100px', resize: 'vertical' }}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="apollo-btn apollo-btn-primary"
              style={{ padding: '1rem 1.5rem', height: '60px' }}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      <ApolloFooter />
    </div>
  );
};

export default Chat;
