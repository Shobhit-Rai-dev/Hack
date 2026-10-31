import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Calendar, Plus, AlertCircle, X } from 'lucide-react';

export default function Plans() {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [billingFrequency, setBillingFrequency] = useState('Monthly');
  const [minimumQuantity, setMinimumQuantity] = useState(1);
  const [behaviorAtEnd, setBehaviorAtEnd] = useState('Close automatically');

  const fetchPlans = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/plans');
      setPlans(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve plans.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/plans', 'POST', {
        name,
        description,
        billing_frequency: billingFrequency,
        minimum_quantity: parseInt(minimumQuantity, 10),
        behavior_at_end: behaviorAtEnd
      });
      setShowModal(false);
      setName('');
      setDescription('');
      setBillingFrequency('Monthly');
      setMinimumQuantity(1);
      fetchPlans();
    } catch (err) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Subscription Plans</h1>
          <p className="page-subtitle">Recurring billing cadence definitions, frequencies, and term rules.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> New Plan
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading subscription plans...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchPlans} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Plan Name</th>
                <th>Billing Frequency</th>
                <th>Min Qty</th>
                <th>Term End Policy</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {plans.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 600 }}>
                    {p.name}
                    {p.description && (
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>{p.description}</div>
                    )}
                  </td>
                  <td>
                    <span className="badge badge-info">{p.billing_frequency}</span>
                  </td>
                  <td>{p.minimum_quantity} unit(s)</td>
                  <td>{p.behavior_at_end}</td>
                  <td>
                    {p.is_active ? (
                      <span className="badge badge-active">Active</span>
                    ) : (
                      <span className="badge badge-overdue">Inactive</span>
                    )}
                  </td>
                </tr>
              ))}
              {plans.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No subscription plans configured.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, backgroundColor: 'rgba(53, 39, 25, 0.5)',
          backdropFilter: 'blur(2px)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 100, padding: 16
        }}>
          <div className="card" style={{ width: '100%', maxWidth: 480 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Configure Subscription Plan
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreatePlan} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Plan Name *</label>
                <input type="text" required value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div>
                <label>Billing Cadence *</label>
                <select value={billingFrequency} onChange={(e) => setBillingFrequency(e.target.value)}>
                  <option value="Daily">Daily</option>
                  <option value="Weekly">Weekly</option>
                  <option value="Monthly">Monthly</option>
                  <option value="Yearly">Yearly</option>
                </select>
              </div>
              <div>
                <label>Minimum Subscription Quantity *</label>
                <input type="number" min="1" required value={minimumQuantity} onChange={(e) => setMinimumQuantity(e.target.value)} />
              </div>
              <div>
                <label>Behavior on Contract Expiry</label>
                <select value={behaviorAtEnd} onChange={(e) => setBehaviorAtEnd(e.target.value)}>
                  <option value="Close automatically">Close automatically</option>
                  <option value="Allow manual closure">Allow manual closure</option>
                  <option value="Pause">Pause</option>
                  <option value="Renew when configured">Renew when configured</option>
                </select>
              </div>
              <div>
                <label>Description</label>
                <textarea rows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Plan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}