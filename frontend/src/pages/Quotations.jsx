import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { FileText, Plus, CheckCircle, RotateCw, AlertCircle } from 'lucide-react';

export default function Quotations() {
  const { user } = useAuth();
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [converting, setConverting] = useState(null);

  const fetchQuotations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRequest('/quotations');
      setQuotations(res);
    } catch (e) {
      setError(e.message || 'Failed to fetch quotations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotations();
  }, []);

  const handleConvert = async (id) => {
    if (!window.confirm("Convert this quotation into an active subscription?")) return;
    setConverting(id);
    try {
      const res = await apiRequest(`/quotations/${id}/convert`, 'POST');
      alert(`Quotation successfully converted to Subscription #${res.subscription_number}`);
      fetchQuotations();
    } catch (err) {
      alert(err.message);
    } finally {
      setConverting(null);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="page-title">Quotations</h1>
          <p className="page-subtitle">Commercial agreements, proposal timelines, and subscription conversions.</p>
        </div>
      </div>

      {loading && (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          Retrieving quotation registry...
        </div>
      )}

      {error && (
        <div className="card" style={{ maxWidth: 500, margin: '20px auto', textAlign: 'center', borderLeft: '4px solid var(--error)' }}>
          <AlertCircle size={24} color="#9C3535" style={{ margin: '0 auto 8px' }} />
          <p style={{ color: 'var(--text-secondary)', marginBottom: 12 }}>{error}</p>
          <button onClick={fetchQuotations} className="btn">Retry</button>
        </div>
      )}

      {!loading && !error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Quotation Number</th>
                <th>Customer</th>
                <th>Associated Plan</th>
                <th>Date Issued</th>
                <th>Expiry Date</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Total (₹)</th>
                {user.role !== 'CUSTOMER' && <th style={{ textAlign: 'center' }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {quotations.map((q) => (
                <tr key={q.id}>
                  <td style={{ fontWeight: 600 }}>{q.quotation_number}</td>
                  <td>{q.customer_name}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{q.plan_name || 'Standard'}</td>
                  <td>{q.quotation_date}</td>
                  <td>{q.expiry_date}</td>
                  <td>
                    <span className={`badge badge-${q.status.toLowerCase()}`}>{q.status}</span>
                  </td>
                  <td className="amount-cell">
                    ₹{q.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  {user.role !== 'CUSTOMER' && (
                    <td style={{ textAlign: 'center' }}>
                      {q.status !== 'Converted' ? (
                        <button 
                          onClick={() => handleConvert(q.id)} 
                          className="btn"
                          style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                          disabled={converting === q.id}
                        >
                          <RotateCw size={13} /> {converting === q.id ? 'Converting...' : 'Convert'}
                        </button>
                      ) : (
                        <span style={{ fontSize: '0.78rem', color: 'var(--success)', fontWeight: 600 }}>
                          Converted
                        </span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
              {quotations.length === 0 && (
                <tr>
                  <td colSpan={user.role !== 'CUSTOMER' ? 8 : 7} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                    No quotations registered in this period.
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