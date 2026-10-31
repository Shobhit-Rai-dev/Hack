import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { 
  RotateCw, Feather, Coins, ShieldCheck, 
  Hourglass, FileWarning, AlertCircle 
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [generating, setGenerating] = useState(false);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/dashboard/summary');
      setData(res);
    } catch (e) {
      setError(e.message || 'Unable to retrieve treasury records from the server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const triggerBilling = async () => {
    setGenerating(true);
    try {
      const res = await apiRequest('/invoices/generate', 'POST');
      alert(res.message);
      fetchSummary();
    } catch (err) {
      alert(err.message);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: 48, textAlign: 'center', color: 'var(--text-secondary)' }}>
        <Feather size={32} color="#A98445" style={{ animation: 'bounce 1s infinite' }} />
        <div style={{ marginTop: 12, fontFamily: 'var(--font-editorial)', fontSize: '1.2rem' }}>
          Loading treasury dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ margin: '30px auto', maxWidth: 520, textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
        <AlertCircle size={32} color="#9C3535" style={{ margin: '0 auto 12px' }} />
        <h3 style={{ fontSize: '1.1rem', marginBottom: 8 }}>Ledger Connection Error</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: 16 }}>{error}</p>
        <button onClick={fetchSummary} className="btn">
          <RotateCw size={15} /> Retry Query
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 28, flexWrap: 'wrap', gap: 14 }}>
        <div>
          <div style={{ fontFamily: 'var(--font-script)', fontSize: '1.75rem', color: 'var(--antique-gold)', lineHeight: 1 }}>
            Welcome, {user.full_name}
          </div>
          <h1 className="page-title">Financial Dashboard</h1>
          <p className="page-subtitle">A consolidated overview of subscriptions, recurring revenue, and accounts receivable.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={triggerBilling} className="btn" disabled={generating}>
            <RotateCw size={15} /> {generating ? 'Generating...' : 'Generate Due Invoices'}
          </button>
        )}
      </div>

      {/* KPI Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: 16, marginBottom: 28 }}>
        <div className="card card-burgundy-accent">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.6px', textTransform: 'uppercase' }}>MONTHLY RECURRING REVENUE</span>
            <Coins size={16} color="#762D35" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--primary-accent)', marginTop: 8 }}>
            ₹{data.kpis.monthly_recurring_revenue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Normalized Run Rate</div>
        </div>

        <div className="card card-gold-accent">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.6px', textTransform: 'uppercase' }}>ACTIVE SUBSCRIPTIONS</span>
            <ShieldCheck size={16} color="#426447" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--success)', marginTop: 8 }}>
            {data.kpis.active_subscriptions}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Current Billing Charters</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.6px', textTransform: 'uppercase' }}>PAYMENTS COLLECTED</span>
            <Coins size={16} color="#A98445" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: 8 }}>
            ₹{data.kpis.payments_collected.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Settled Cash</div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.6px', textTransform: 'uppercase' }}>OUTSTANDING BALANCE</span>
            <Hourglass size={16} color="#A56B26" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--warning)', marginTop: 8 }}>
            ₹{data.kpis.outstanding_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Pending Invoice Sum</div>
        </div>

        <div className="card" style={{ borderTop: '3px solid var(--error)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.6px', textTransform: 'uppercase' }}>OVERDUE AMOUNT</span>
            <FileWarning size={16} color="#9C3535" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--error)', marginTop: 8 }}>
            ₹{data.kpis.overdue_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: 4 }}>Past Due Invoices</div>
        </div>
      </div>

      {/* Business Insights */}
      {data.insights && data.insights.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <div className="ornamental-divider">
            <span style={{ fontFamily: 'var(--font-serif-title)', fontSize: '0.82rem', letterSpacing: '1px', color: 'var(--antique-gold)' }}>
              BUSINESS INSIGHTS & AUDIT
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(310px, 1fr))', gap: 14 }}>
            {data.insights.map((ins) => (
              <div 
                key={ins.id} 
                className="card" 
                style={{ 
                  borderLeft: `4px solid ${ins.severity === 'CRITICAL' ? 'var(--error)' : ins.severity === 'WARNING' ? 'var(--warning)' : 'var(--antique-gold)'}`,
                  backgroundColor: '#FFFDF9'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{ins.title}</div>
                  <span className={`badge badge-${ins.severity.toLowerCase()}`}>{ins.severity}</span>
                </div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '8px 0', lineHeight: 1.4 }}>
                  {ins.explanation}
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--primary-accent)', fontWeight: 600 }}>
                  <span style={{ color: 'var(--text-muted)' }}>Recommended:</span> {ins.action}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revenue Chart */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div>
            <h3 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.25rem', fontWeight: 700 }}>Collections Realization</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Payments recorded against confirmed invoices</p>
          </div>
          <div style={{ display: 'flex', gap: 12, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 10, height: 10, backgroundColor: '#762D35', borderRadius: 2 }}></span> Settled Cash (₹)
            </span>
          </div>
        </div>

        <div style={{ height: 260 }}>
          {data.revenue_trend && data.revenue_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.revenue_trend} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid stroke="#E5D7BF" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" stroke="#92806A" fontSize={12} tickLine={false} />
                <YAxis stroke="#92806A" fontSize={12} tickLine={false} />
                <Tooltip 
                  formatter={(val) => [`₹${Number(val).toLocaleString('en-IN')}`, 'Collected']}
                  contentStyle={{ 
                    backgroundColor: '#FFFAEF', 
                    border: '1px solid #D8C5A2',
                    borderRadius: 4,
                    color: '#352719'
                  }} 
                />
                <Bar dataKey="total" fill="#762D35" radius={[3, 3, 0, 0]} maxBarSize={48} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No recorded payments found for trend visualization.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}