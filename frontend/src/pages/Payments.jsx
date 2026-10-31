import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { CreditCard, Plus, AlertCircle, X } from 'lucide-react';

export default function Payments() {
  const { user } = useAuth();
  const [payments, setPayments] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form State
  const [invoiceId, setInvoiceId] = useState('');
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('Bank Transfer');
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split('T')[0]);
  const [note, setNote] = useState('');

  const fetchPayments = async () => {
    setLoading(true);
    setError(null);
    try {
      const [pmts, invs] = await Promise.all([
        apiRequest('/payments'),
        user.role !== 'CUSTOMER' ? apiRequest('/invoices') : Promise.resolve([])
      ]);
      setPayments(pmts);
      // Filter unpaid invoices for selection
      setInvoices(invs.filter((i) => i.status !== 'Paid' && i.status !== 'Cancelled'));
      if (invs.length > 0) setInvoiceId(invs[0].id);
    } catch (err) {
      setError(err.message || 'Failed to retrieve payment records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  const handleRecordPayment = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiRequest('/payments', 'POST', {
        invoice_id: parseInt(invoiceId, 10),
        payment_method: paymentMethod,
        amount: parseFloat(amount),
        payment_date: paymentDate,
        note
      });
      setShowModal(false);
      setAmount('');
      setNote('');
      fetchPayments();
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
          <h1 className="page-title">{user.role === 'CUSTOMER' ? 'Payment History' : 'Payments'}</h1>
          <p className="page-subtitle">Discharged settlements, cash collections, and transactional audit trails.</p>
        </div>
        {user.role !== 'CUSTOMER' && (
          <button onClick={() => setShowModal(true)} className="btn">
            <Plus size={16} /> Record Payment
          </button>
        )}
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Auditing payment records...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="var(--error)" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchPayments} className="btn">Retry Query</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Payment Ref</th>
                <th>Invoice Number</th>
                {user.role !== 'CUSTOMER' && <th>Customer</th>}
                <th>Date Settled</th>
                <th>Method</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Amount Paid (₹)</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 600 }}>{p.payment_reference}</td>
                  <td>{p.invoice_number}</td>
                  {user.role !== 'CUSTOMER' && <td>{p.customer_name}</td>}
                  <td>{p.payment_date}</td>
                  <td>
                    <span className="badge badge-draft">{p.payment_method}</span>
                  </td>
                  <td>
                    <span className="badge badge-paid">{p.status}</span>
                  </td>
                  <td className="amount-cell" style={{ color: 'var(--success)' }}>
                    ₹{Number(p.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
              {payments.length === 0 && (
                <tr>
                  <td colSpan={user.role !== 'CUSTOMER' ? 7 : 6} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No payment records inscribed to date.
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
                Record Payment Settlement
              </h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleRecordPayment} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label>Select Invoiced Account *</label>
                <select value={invoiceId} onChange={(e) => setInvoiceId(e.target.value)}>
                  {invoices.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      {inv.invoice_number} — {inv.customer_name} (Due: ₹{inv.balance_due})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label>Amount (₹) *</label>
                  <input type="number" step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} />
                </div>
                <div>
                  <label>Payment Method *</label>
                  <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="UPI">UPI</option>
                    <option value="Card">Card</option>
                    <option value="Cash">Cash</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label>Date of Payment *</label>
                <input type="date" required value={paymentDate} onChange={(e) => setPaymentDate(e.target.value)} />
              </div>

              <div>
                <label>Audit Memo / Transaction Reference</label>
                <textarea rows={2} value={note} onChange={(e) => setNote(e.target.value)} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn" disabled={submitting}>
                  {submitting ? 'Recording...' : 'Commit Payment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}