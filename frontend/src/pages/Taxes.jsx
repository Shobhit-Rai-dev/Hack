import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Scale, Plus, AlertCircle, X } from 'lucide-react';

export default function Taxes() {
  const { user } = useAuth();
  const [taxes, setTaxes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [name, setName] = useState('');
  const [rate, setRate] = useState('');
  const [applicableTo, setApplicableTo] = useState('All');

  const fetchTaxes = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/taxes');
      setTaxes(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve tax configurations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTaxes();
  }, []);

  const handleCreateTax = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/taxes', 'POST', {
        name,
        rate: parseFloat(rate),
        applicable_to: applicableTo
      });
      setShowModal(false);
      setName('');
      setRate('');
      fetchTaxes();
    } catch (err) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const toggleStatus = async (id) => {
    try {
      await apiRequest(`/taxes/${id}/status`, 'PATCH');
      fetchTaxes();
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Taxes</h1>
          <p className="page-subtitle">Statutory rates, percentage charges, and invoice tax rule engines.</p>
        </div>
        {user.role === 'ADMIN' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> New Tax Rule
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Retrieving statutory tax schedule...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchTaxes} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Tax Description</th>
                <th>Rate (%)</th>
                <th>Scope</th>
                <th>Status</th>
                {user.role === 'ADMIN' && <th style={{ textAlign: 'center' }}>Toggle</th>}
              </tr>
            </thead>
            <tbody>
              {taxes.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 600 }}>{t.name}</td>
                  <td style={{ fontWeight: 600, color: 'var(--primary-accent)' }}>{t.rate}%</td>
                  <td>{t.applicable_to}</td>
                  <td>
                    {t.is_active ? (
                      <span className="badge badge-active">Active</span>
                    ) : (
                      <span className="badge badge-overdue">Disabled</span>
                    )}
                  </td>
                  {user.role === 'ADMIN' && (
                    <td style={{ textAlign: 'center' }}>
                      <button
                        onClick={() => toggleStatus(t.id)}
                        className="btn btn-secondary"
                        style={{ padding: '3px 8px', fontSize: '0.72rem' }}
                      >
                        {t.is_active ? 'Disable' : 'Enable'}
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {taxes.length === 0 && (
                <tr>
                  <td colSpan={user.role === 'ADMIN' ? 5 : 4} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No statutory tax rates configured.
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
          <div className="card" style={{ width: '100%', maxWidth: 440 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Define Tax Rule
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateTax} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Tax Name / Classification *</label>
                <input type="text" required placeholder="e.g. GST 18%" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div>
                <label>Percentage Rate (%) *</label>
                <input type="number" step="0.01" required placeholder="18.0" value={rate} onChange={(e) => setRate(e.target.value)} />
              </div>
              <div>
                <label>Applicable Scope</label>
                <select value={applicableTo} onChange={(e) => setApplicableTo(e.target.value)}>
                  <option value="All">All Invoices & Products</option>
                  <option value="Services">Services Only</option>
                  <option value="Physical">Physical Goods Only</option>
                </select>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Tax Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}