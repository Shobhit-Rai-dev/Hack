import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { RotateCw, AlertCircle, Pause, Play, XCircle } from 'lucide-react';

export default function Subscriptions() {
  const { user } = useAuth();
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSubscriptions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/subscriptions');
      setSubscriptions(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve subscriptions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const handleStatusChange = async (id, newStatus) => {
    if (!window.confirm(`Update subscription status to ${newStatus}?`)) return;
    try {
      await apiRequest(`/subscriptions/${id}/status?status=${newStatus}`, 'PATCH');
      fetchSubscriptions();
    } catch (err) {
      alert(err.message);
    }
  };

  const getStatusBadge = (status) => {
    const s = status.toLowerCase();
    return <span className={`badge badge-${s}`}>{status}</span>;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">{user.role === 'CUSTOMER' ? 'My Subscriptions' : 'Subscriptions'}</h1>
          <p className="page-subtitle">Active contracts, recurring billing terms, and renewal tracking.</p>
        </div>
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Accessing active subscriptions registry...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchSubscriptions} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Subscription No</th>
                {user.role !== 'CUSTOMER' && <th>Customer</th>}
                <th>Plan Cadence</th>
                <th>Start Date</th>
                <th>Next Billing Date</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Recurring Total (₹)</th>
                {user.role !== 'CUSTOMER' && <th style={{ textAlign: 'center' }}>Manage</th>}
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600 }}>{s.subscription_number}</td>
                  {user.role !== 'CUSTOMER' && <td>{s.customer_name}</td>}
                  <td>
                    <span className="badge badge-info">{s.plan_name} ({s.billing_frequency})</span>
                  </td>
                  <td>{s.start_date}</td>
                  <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{s.next_billing_date}</td>
                  <td>{getStatusBadge(s.status)}</td>
                  <td className="amount-cell">
                    ₹{Number(s.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  {user.role !== 'CUSTOMER' && (
                    <td style={{ textAlign: 'center' }}>
                      <div style={{ display: 'flex', gap: 6, justifyContent: 'center' }}>
                        {s.status === 'Active' ? (
                          <button
                            onClick={() => handleStatusChange(s.id, 'Paused')}
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                            title="Pause Subscription"
                          >
                            <Pause size={13} />
                          </button>
                        ) : s.status === 'Paused' ? (
                          <button
                            onClick={() => handleStatusChange(s.id, 'Active')}
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
                            title="Resume Subscription"
                          >
                            <Play size={13} />
                          </button>
                        ) : null}

                        {s.status !== 'Closed' && (
                          <button
                            onClick={() => handleStatusChange(s.id, 'Closed')}
                            className="btn btn-secondary"
                            style={{ padding: '4px 8px', fontSize: '0.75rem', color: 'var(--error)' }}
                            title="Close Subscription"
                          >
                            <XCircle size={13} />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
              {subscriptions.length === 0 && (
                <tr>
                  <td colSpan={user.role !== 'CUSTOMER' ? 8 : 6} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No subscriptions registered.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}