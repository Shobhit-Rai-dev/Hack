import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Box, Plus, AlertCircle, X } from 'lucide-react';

export default function Products() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [name, setName] = useState('');
  const [productType, setProductType] = useState('Service');
  const [salesPrice, setSalesPrice] = useState('');
  const [costPrice, setCostPrice] = useState('');
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/products');
      setProducts(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve products catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/products', 'POST', {
        name,
        product_type: productType,
        sales_price: parseFloat(salesPrice),
        cost_price: parseFloat(costPrice || '0'),
        description,
        notes
      });
      setShowModal(false);
      setName('');
      setSalesPrice('');
      setCostPrice('');
      setDescription('');
      setNotes('');
      fetchProducts();
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
          <h1 className="page-title">Products & Services</h1>
          <p className="page-subtitle">Standardized catalog of billable goods, subscription items, and services.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> New Product
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Accessing products catalog...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchProducts} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Type</th>
                <th>Description</th>
                {user.role !== 'CUSTOMER' && <th style={{ textAlign: 'right' }}>Cost Price (₹)</th>}
                <th style={{ textAlign: 'right' }}>Sales Price (₹)</th>
                <th>Variants</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 600 }}>{p.name}</td>
                  <td>
                    <span className="badge badge-info">{p.product_type}</span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)' }}>{p.description || '—'}</td>
                  {user.role !== 'CUSTOMER' && (
                    <td className="amount-cell" style={{ color: 'var(--text-muted)' }}>
                      ₹{Number(p.cost_price || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </td>
                  )}
                  <td className="amount-cell">
                    ₹{Number(p.sales_price || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td>
                    {p.variants && p.variants.length > 0 ? (
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {p.variants.map((v) => (
                          <span key={v.id} className="badge badge-draft">
                            {v.variant_name} (+₹{v.price_adjustment})
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Standard</span>
                    )}
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={user.role !== 'CUSTOMER' ? 6 : 5} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No products registered in catalog.
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
          <div className="card" style={{ width: '100%', maxWidth: 500 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Define New Catalog Item
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Product Name *</label>
                <input type="text" required value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div>
                <label>Product Classification *</label>
                <select value={productType} onChange={(e) => setProductType(e.target.value)}>
                  <option value="Service">Service</option>
                  <option value="Digital Product">Digital Product</option>
                  <option value="Physical Product">Physical Product</option>
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Sales Price (₹) *</label>
                  <input type="number" step="0.01" required value={salesPrice} onChange={(e) => setSalesPrice(e.target.value)} />
                </div>
                <div>
                  <label>Cost Price (₹)</label>
                  <input type="number" step="0.01" value={costPrice} onChange={(e) => setCostPrice(e.target.value)} />
                </div>
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
                  {submitting ? 'Creating...' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}