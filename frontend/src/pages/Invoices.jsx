import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ReceiptText, Printer, CheckCircle2, X } from 'lucide-react';

export default function Invoices() {
  const { user } = useAuth();
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  const fetchInvoices = async () => {
    try {
      const res = await apiRequest('/invoices');
      setInvoices(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const openInvoice = async (id) => {
    try {
      const data = await apiRequest(`/invoices/${id}`);
      setSelectedInvoice(data);
    } catch (err) {
      alert(err.message);
    }
  };

  const getStatusBadge = (status) => {
    const s = status.toLowerCase().replace(' ', '-');
    return <span className={`badge badge-${s}`}>{status}</span>;
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 24 }}>
        <div>
          <h1 className="page-title">Debenture Invoices</h1>
          <p className="page-subtitle">Formal record of accounts rendered, period liabilities, and discharge of dues.</p>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Invoice Ref</th>
              <th>Debtor / Guild</th>
              <th>Charter No</th>
              <th>Term Due</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Total (₹)</th>
              <th style={{ textAlign: 'right' }}>Due Balance (₹)</th>
              <th style={{ textAlign: 'center' }}>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id}>
                <td style={{ fontWeight: 600 }}>{inv.invoice_number}</td>
                <td>{inv.customer_name}</td>
                <td style={{ color: 'var(--text-muted)' }}>{inv.subscription_number}</td>
                <td>{inv.due_date}</td>
                <td>{getStatusBadge(inv.status)}</td>
                <td className="amount-cell">₹{inv.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td className="amount-cell" style={{ color: inv.balance_due > 0 ? 'var(--error)' : 'var(--success)' }}>
                  ₹{inv.balance_due.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
                <td style={{ textAlign: 'center' }}>
                  <button onClick={() => openInvoice(inv.id)} className="btn btn-secondary" style={{ padding: '5px 10px', fontSize: '0.78rem' }}>
                    View Ledger
                  </button>
                </td>
              </tr>
            ))}
            {invoices.length === 0 && (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                  No debenture invoices inscribed to date.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Printable Ledger Invoice Modal */}
      {selectedInvoice && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(53, 39, 25, 0.45)', backdropFilter: 'blur(2px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 16
        }}>
          <div className="card" style={{ width: '100%', maxWidth: 740, maxHeight: '90vh', overflowY: 'auto', padding: 36, border: '1px solid var(--gold-border)' }}>
            <div className="no-print" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
              <button onClick={() => window.print()} className="btn btn-gold">
                <Printer size={15} /> Print Ledger Document
              </button>
              <button onClick={() => setSelectedInvoice(null)} className="btn btn-secondary">
                <X size={15} /> Close
              </button>
            </div>

            {/* Printable Document Sheet */}
            <div style={{ border: '1px solid var(--standard-border)', padding: 32, backgroundColor: '#FFFDFA' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid var(--antique-gold)', paddingBottom: 16, marginBottom: 20 }}>
                <div>
                  <div className="brand" style={{ fontSize: '1.4rem' }}>Subscript<span>IQ</span></div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
                    Imperial Treasury &bull; Debenture Record
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'var(--font-serif-title)', fontSize: '1.1rem', fontWeight: 700 }}>{selectedInvoice.invoice_number}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Dated: {selectedInvoice.issue_date}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--error)' }}>Due By: {selectedInvoice.due_date}</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24, fontSize: '0.85rem' }}>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.72rem' }}>BILLED UNTO:</div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: 2 }}>{selectedInvoice.customer_name}</div>
                  <div>{selectedInvoice.company_name}</div>
                  <div style={{ color: 'var(--text-secondary)' }}>{selectedInvoice.billing_address}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', fontSize: '0.72rem' }}>CHARTER REF:</div>
                  <div style={{ fontWeight: 600 }}>{selectedInvoice.subscription_number}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    Period: {selectedInvoice.billing_period_start} to {selectedInvoice.billing_period_end}
                  </div>
                </div>
              </div>

              {/* Items Table */}
              <table style={{ marginBottom: 20 }}>
                <thead>
                  <tr>
                    <th>Line Item Description</th>
                    <th style={{ textAlign: 'center' }}>Qty</th>
                    <th style={{ textAlign: 'right' }}>Unit Price (₹)</th>
                    <th style={{ textAlign: 'right' }}>Line Total (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedInvoice.items?.map((it) => (
                    <tr key={it.id}>
                      <td>{it.description}</td>
                      <td style={{ textAlign: 'center' }}>{it.quantity}</td>
                      <td className="amount-cell">₹{it.unit_price.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                      <td className="amount-cell">₹{it.line_total.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Totals Summary */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
                <div style={{ width: 260, fontSize: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                    <span>Subtotal:</span>
                    <span>₹{selectedInvoice.subtotal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', color: 'var(--success)' }}>
                    <span>Concession (Discount):</span>
                    <span>-₹{selectedInvoice.discount_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', color: 'var(--text-secondary)' }}>
                    <span>Imperial Levy (Tax):</span>
                    <span>+₹{selectedInvoice.tax_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div style={{ 
                    display: 'flex', justifyContent: 'space-between', padding: '8px 0', 
                    borderTop: '1px solid var(--standard-border)', 
                    borderBottom: '2px solid var(--text-primary)',
                    fontWeight: 700, fontSize: '1rem', marginTop: 6 
                  }}>
                    <span>Debenture Total:</span>
                    <span>₹{selectedInvoice.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', color: 'var(--success)', fontWeight: 600 }}>
                    <span>Paid to Date:</span>
                    <span>₹{selectedInvoice.amount_paid.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', color: selectedInvoice.balance_due > 0 ? 'var(--error)' : 'var(--text-muted)', fontWeight: 700 }}>
                    <span>Outstanding Dues:</span>
                    <span>₹{selectedInvoice.balance_due.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}