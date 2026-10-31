import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { FileText, Plus, AlertCircle, X } from 'lucide-react';

export default function QuotationTemplates() {
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [products, setProducts] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Template Form
  const [name, setName] = useState('');
  const [planId, setPlanId] = useState('');
  const [validityDays, setValidityDays] = useState(30);
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState([{ product_id: '', quantity: 1, description: '' }]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [tData, prodData, planData] = await Promise.all([
        apiRequest('/quotation-templates'),
        apiRequest('/products'),
        apiRequest('/plans')
      ]);
      setTemplates(tData);
      setProducts(prodData);
      setPlans(planData);
      if (planData.length > 0) setPlanId(planData[0].id);
    } catch (err) {
      setError(err.message || 'Failed to load quotation templates.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const addItemLine = () => {
    setItems([...items, { product_id: products[0]?.id || '', quantity: 1, description: '' }]);
  };

  const updateItemLine = (idx, field, val) => {
    const next = [...items];
    next[idx][field] = val;
    setItems(next);
  };

  const removeItemLine = (idx) => {
    setItems(items.filter((_, i) => i !== idx));
  };

  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/quotation-templates', 'POST', {
        name,
        plan_id: parseInt(planId, 10),
        validity_days: parseInt(validityDays, 10),
        notes,
        items: items.map((it) => ({
          product_id: parseInt(it.product_id, 10),
          quantity: parseInt(it.quantity, 10),
          description: it.description || null
        }))
      });
      setShowModal(false);
      setName('');
      setNotes('');
      fetchData();
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
          <h1 className="page-title">Quotation Templates</h1>
          <p className="page-subtitle">Standardized quotation packages to accelerate subscription onboarding.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> New Template
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Retrieving quotation templates...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchData} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Template Name</th>
                <th>Associated Plan</th>
                <th>Validity (Days)</th>
                <th>Included Products</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {templates.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 600 }}>{t.name}</td>
                  <td>
                    <span className="badge badge-info">{t.plan_name} ({t.billing_frequency})</span>
                  </td>
                  <td>{t.validity_days} days</td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                      {t.items?.map((it) => (
                        <span key={it.id} style={{ fontSize: '0.82rem' }}>
                          • {it.quantity}x {it.product_name}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{t.notes || '—'}</td>
                </tr>
              ))}
              {templates.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No quotation templates configured.
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
          <div className="card" style={{ width: '100%', maxWidth: 560, maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Build Quotation Template
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateTemplate} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Template Name *</label>
                <input type="text" required value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Base Subscription Plan *</label>
                  <select value={planId} onChange={(e) => setPlanId(e.target.value)}>
                    {plans.map((p) => (
                      <option key={p.id} value={p.id}>{p.name} ({p.billing_frequency})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label>Validity Period (Days) *</label>
                  <input type="number" min="1" required value={validityDays} onChange={(e) => setValidityDays(e.target.value)} />
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <label style={{ margin: 0 }}>Line Items</label>
                  <button type="button" onClick={addItemLine} className="btn btn-secondary" style={{ padding: '3px 8px', fontSize: '0.72rem' }}>
                    + Add Item
                  </button>
                </div>
                {items.map((it, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
                    <select
                      style={{ flex: 2 }}
                      value={it.product_id}
                      onChange={(e) => updateItemLine(idx, 'product_id', e.target.value)}
                    >
                      <option value="">Select Product...</option>
                      {products.map((p) => (
                        <option key={p.id} value={p.id}>{p.name} (₹{p.sales_price})</option>
                      ))}
                    </select>
                    <input
                      type="number"
                      min="1"
                      style={{ flex: 1 }}
                      placeholder="Qty"
                      value={it.quantity}
                      onChange={(e) => updateItemLine(idx, 'quantity', e.target.value)}
                    />
                    {items.length > 1 && (
                      <button type="button" onClick={() => removeItemLine(idx)} className="btn btn-secondary" style={{ padding: '8px 10px' }}>
                        <X size={14} />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <div>
                <label>Standard Notes / Terms</label>
                <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Template'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}