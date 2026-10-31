import React, { useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { BookOpen, ShieldCheck } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await apiRequest('/auth/login', 'POST', { email, password });
      login(res.access_token, res.user);
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (roleEmail, rolePwd) => {
    setEmail(roleEmail);
    setPassword(rolePwd);
  };

  return (
    <div style={{ 
      display: 'flex', 
      minHeight: '100vh', 
      alignItems: 'center', 
      justifyContent: 'center', 
      backgroundColor: 'var(--bg-main)',
      padding: 16
    }}>
      <div className="card" style={{ 
        width: '100%', 
        maxWidth: 440, 
        padding: '38px 34px', 
        border: '1px solid var(--gold-border)',
        boxShadow: '0 8px 24px rgba(53, 39, 25, 0.08)'
      }}>
        {/* Brand Crest */}
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ 
            display: 'inline-flex', 
            padding: 12, 
            borderRadius: '50%', 
            backgroundColor: 'var(--bg-card-elevated)', 
            border: '1px solid var(--gold-border)',
            marginBottom: 10 
          }}>
            <BookOpen color="#762D35" size={28} strokeWidth={2.2} />
          </div>
          <div className="brand" style={{ justifyContent: 'center', fontSize: '1.6rem' }}>
            Subscript<span>IQ</span>
          </div>
          <div style={{ 
            fontFamily: 'var(--font-script)', 
            fontSize: '1.3rem', 
            color: 'var(--antique-gold)', 
            marginTop: 4 
          }}>
            Every covenant accounted for. Every coin remembered.
          </div>
        </div>

        {error && (
          <div style={{ 
            color: 'var(--error)', 
            backgroundColor: 'rgba(156, 53, 53, 0.08)', 
            border: '1px solid rgba(156, 53, 53, 0.25)', 
            padding: 10, 
            borderRadius: 4, 
            marginBottom: 16, 
            fontSize: '0.85rem' 
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label>Email Address</label>
            <input 
              type="email" 
              placeholder="e.g. admin@subscriptiq.com"
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div>
            <label>Password</label>
            <input 
              type="password" 
              placeholder="••••••••"
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          <button type="submit" className="btn" style={{ justifyContent: 'center', padding: '11px 0', marginTop: 6 }} disabled={loading}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Credentials Section */}
        <div style={{ 
          marginTop: 22, 
          padding: 12, 
          backgroundColor: 'var(--bg-card-elevated)', 
          border: '1px solid var(--standard-border)',
          borderRadius: 4, 
          fontSize: '0.76rem', 
          color: 'var(--text-secondary)' 
        }}>
          <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 5 }}>
            <ShieldCheck size={14} color="#762D35" /> Quick Fill Demo Accounts:
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <button 
              type="button" 
              onClick={() => fillCredentials('admin@subscriptiq.com', 'Admin@123!')}
              className="btn btn-secondary" 
              style={{ padding: '3px 8px', fontSize: '0.72rem' }}
            >
              Admin
            </button>
            <button 
              type="button" 
              onClick={() => fillCredentials('staff@subscriptiq.com', 'Staff@123!')}
              className="btn btn-secondary" 
              style={{ padding: '3px 8px', fontSize: '0.72rem' }}
            >
              Staff
            </button>
            <button 
              type="button" 
              onClick={() => fillCredentials('bruce@waynecorp.com', 'Customer@123!')}
              className="btn btn-secondary" 
              style={{ padding: '3px 8px', fontSize: '0.72rem' }}
            >
              Customer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}