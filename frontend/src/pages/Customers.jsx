import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Users, Plus, Search, AlertCircle, X, ShieldCheck } from 'lucide-react';

export default function Customers() {
  const { user } = useAuth();
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form State
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [billingAddress, setBillingAddress] = useState('');
  const [createPortal, setCreatePortal] = useState(false);
  const [portalPassword, setPortalPassword] = useState('');

  const fetchCustomers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/customers');
      setCustomers(res);
    } catch (err) {
      setError(err.message || 'Failed to retrieve customer accounts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const handleCreateCustomer = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/customers', 'POST', {
        full_name: fullName,
        email,
        phone: phone || null,
        company_name: companyName || null,
        billing_address: billingAddress || null,
        create_portal_account: createPortal,
        portal_password: createPortal ? portalPassword : null
      });
      setShowModal(false);
      setFullName('');
      setEmail('');
      setPhone('');
      setCompanyName('');
      setBillingAddress('');
      setCreatePortal(false);
      setPortalPassword('');
      fetchCustomers();
    } catch (err) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const filtered = customers.filter((c) =>
    c.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    c.email?.toLowerCase().includes(search.toLowerCase()) ||
    c.company_name?.toLowerCase().includes(search.toLowerCase()) ||
    c.customer_number?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Customers</h1>
          <p className="page-subtitle">Directory of registered commercial accounts, contacts, and billing ledgers.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> Register Customer
          </button>
        )}
      </div>

      <div style={{ marginBottom: 16, maxWidth: 360, position: 'relative' }}>
        <input
          type="text"
          placeholder="Search by name, email, or company..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ paddingLeft: 34 }}
        />
        <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 10, top: 12 }} />
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Reading customer registry...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchCustomers} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Full Name</th>
                <th>Company</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Portal Access</th>
                <th style={{ textAlign: 'right' }}>Outstanding Dues</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 600 }}>{c.customer_number}</td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.full_name}</td>
                  <td>{c.company_name || '—'}</td>
                  <td>{c.email}</td>
                  <td>{c.phone || '—'}</td>
                  <td>
                    {c.user_id ? (
                      <span className="badge badge-active"><ShieldCheck size={12} /> Enabled</span>
                    ) : (
                      <span className="badge badge-draft">Direct Billing</span>
                    )}
                  </td>
                  <td className="amount-cell" style={{ color: c.total_balance_due > 0 ? 'var(--error)' : 'var(--success)' }}>
                    ₹{Number(c.total_balance_due || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No customer accounts match the query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Registration Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, backgroundColor: 'rgba(53, 39, 25, 0.5)',
          backdropFilter: 'blur(2px)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 100, padding: 16
        }}>
          <div className="card" style={{ width: '100%', maxWidth: 520, maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h2 style={{ fontFamily: 'var(--font-editorial)', fontSize: '1.4rem', fontWeight: 700 }}>
                Register Commercial Account
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateCustomer} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Legal Name *</label>
                <input type="text" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
              </div>
              <div>
                <label>Email Address *</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Company / Organization</label>
                  <input type="text" value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
                </div>
                <div>
                  <label>Contact Phone</label>
                  <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} />
                </div>
              </div>
              <div>
                <label>Billing Address</label>
                <textarea rows={2} value={billingAddress} onChange={(e) => setBillingAddress(e.target.value)} />
              </div>

              <div style={{ borderTop: '1px solid var(--standard-border)', paddingTop: 14 }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', textTransform: 'none', fontSize: '0.85rem' }}>
                  <input
                    type="checkbox"
                    checked={createPortal}
                    onChange={(e) => setCreatePortal(e.target.checked)}
                    style={{ width: 'auto' }}
                  />
                  <span>Provision Customer Portal Credentials</span>
                </label>
              </div>

              {createPortal && (
                <div>
                  <label>Initial Portal Password *</label>
                  <input
                    type="password"
                    required
                    placeholder="Min 8 chars, Upper, Lower, Special"
                    value={portalPassword}
                    onChange={(e) => setPortalPassword(e.target.value)}
                  />
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Registering...' : 'Save Customer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}