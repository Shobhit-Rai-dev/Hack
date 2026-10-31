import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Percent, Plus, AlertCircle, X, ShieldAlert } from 'lucide-react';

export default function Discounts() {
  const { user } = useAuth();
  const [discounts, setDiscounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [name, setName] = useState('');
  const [discountType, setDiscountType] = useState('Percentage');
  const [discountValue, setDiscountValue] = useState('');
  const [minPurchase, setMinPurchase] = useState('0');
  const [usageLimit, setUsageLimit] = useState('');

  const fetchDiscounts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/discounts');
      setDiscounts(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve discount rules.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscounts();
  }, []);

  const handleCreateDiscount = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/discounts', 'POST', {
        name,
        discount_type: discountType,
        discount_value: parseFloat(discountValue),
        minimum_purchase: parseFloat(minPurchase || '0'),
        usage_limit: usageLimit ? parseInt(usageLimit, 10) : null
      });
      setShowModal(false);
      setName('');
      setDiscountValue('');
      fetchDiscounts();
    } catch (err) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const toggleStatus = async (id) => {
    try {
      await apiRequest(`/discounts/${id}/status`, 'PATCH');
      fetchDiscounts();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Discounts</h1>
          <p className="page-subtitle">Commercial discount rules, percentage deductions, and purchase thresholds.</p>
        </div>
        {user.role === 'ADMIN' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> New Discount Rule
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Retrieving discount registry...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchDiscounts} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Rule Name</th>
                <th>Type</th>
                <th>Discount Value</th>
                <th>Min. Purchase (₹)</th>
                <th>Usage Count</th>
                <th>Status</th>
                {user.role === 'ADMIN' && <th style={{ textAlign: 'center' }}>Toggle</th>}
              </tr>
            </thead>
            <tbody>
              {discounts.map((d) => (
                <tr key={d.id}>
                  <td style={{ fontWeight: 600 }}>{d.name}</td>
                  <td>
                    <span className="badge badge-info">{d.discount_type}</span>
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--primary-accent)' }}>
                    {d.discount_type === 'Percentage' ? `${d.discount_value}%` : `₹${d.discount_value}`}
                  </td>
                  <td>₹{Number(d.minimum_purchase).toLocaleString('en-IN')}</td>
                  <td>{d.usage_count} {d.usage_limit ? `/ ${d.usage_limit}` : ''}</td>
                  <td>
                    {d.is_active ? (
                      <span className="badge badge-active">Active</span>
                    ) : (
                      <span className="badge badge-overdue">Disabled</span>
                    )}
                  </td>
                  {user.role === 'ADMIN' && (
                    <td style={{ textAlign: 'center' }}>
                      <button
                        onClick={() => toggleStatus(d.id)}
                        className="btn btn-secondary"
                        style={{ padding: '3px 8px', fontSize: '0.72rem' }}
                      >
                        {d.is_active ? 'Disable' : 'Enable'}
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {discounts.length === 0 && (
                <tr>
                  <td colSpan={user.role === 'ADMIN' ? 7 : 6} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No discount rules configured.
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
          <div className="card" style={{ width: '100%', maxWidth: 460 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Configure Discount Rule
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateDiscount} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Rule Code / Name *</label>
                <input type="text" required placeholder="e.g. ANNUAL10" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Type *</label>
                  <select value={discountType} onChange={(e) => setDiscountType(e.target.value)}>
                    <option value="Percentage">Percentage</option>
                    <option value="Fixed">Fixed Amount</option>
                  </select>
                </div>
                <div>
                  <label>Value *</label>
                  <input type="number" step="0.01" required value={discountValue} onChange={(e) => setDiscountValue(e.target.value)} />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Minimum Purchase (₹)</label>
                  <input type="number" step="0.01" value={minPurchase} onChange={(e) => setMinPurchase(e.target.value)} />
                </div>
                <div>
                  <label>Usage Limit</label>
                  <input type="number" placeholder="Optional" value={usageLimit} onChange={(e) => setUsageLimit(e.target.value)} />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Discount Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}