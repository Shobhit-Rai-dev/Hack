import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, Users, Box, Calendar, FileText, 
  RotateCw, Receipt, CreditCard, Percent, Scale, 
  ShieldCheck, LogOut, BookOpen, X
} from 'lucide-react';

export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <>
      {isOpen && <div className="mobile-backdrop" onClick={onClose} aria-hidden="true" />}
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        {/* Header & Brand */}
        <div style={{ padding: '20px 20px', borderBottom: '1px solid var(--standard-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div className="brand">
            <BookOpen color="#762D35" size={24} strokeWidth={2.2} />
            <div>
              Subscript<span>IQ</span>
              <div className="brand-flourish">The Royal Ledger</div>
            </div>
          </div>
          <button 
            onClick={onClose} 
            className="no-print" 
            style={{ 
              display: 'none', 
              background: 'none', 
              border: 'none', 
              cursor: 'pointer', 
              color: 'var(--text-secondary)' 
            }}
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation items */}
        <div style={{ flex: 1, padding: '14px 0', overflowY: 'auto' }}>
          <NavLink to="/" className="nav-link" onClick={onClose}>
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>

          {user.role !== 'CUSTOMER' && (
            <>
              <div style={{ padding: '16px 20px 6px', fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase' }}>
                Operations
              </div>
              <NavLink to="/customers" className="nav-link" onClick={onClose}>
                <Users size={18} />
                <span>Customers</span>
              </NavLink>
              <NavLink to="/products" className="nav-link" onClick={onClose}>
                <Box size={18} />
                <span>Products</span>
              </NavLink>
              <NavLink to="/plans" className="nav-link" onClick={onClose}>
                <Calendar size={18} />
                <span>Subscription Plans</span>
              </NavLink>
              <NavLink to="/quotation-templates" className="nav-link" onClick={onClose}>
                <FileText size={18} />
                <span>Quotation Templates</span>
              </NavLink>
              <NavLink to="/quotations" className="nav-link" onClick={onClose}>
                <FileText size={18} />
                <span>Quotations</span>
              </NavLink>
              <NavLink to="/subscriptions" className="nav-link" onClick={onClose}>
                <RotateCw size={18} />
                <span>Subscriptions</span>
              </NavLink>
              <NavLink to="/invoices" className="nav-link" onClick={onClose}>
                <Receipt size={18} />
                <span>Invoices</span>
              </NavLink>
              <NavLink to="/payments" className="nav-link" onClick={onClose}>
                <CreditCard size={18} />
                <span>Payments</span>
              </NavLink>

              {user.role === 'ADMIN' && (
                <>
                  <div style={{ padding: '16px 20px 6px', fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase' }}>
                    Management
                  </div>
                  <NavLink to="/discounts" className="nav-link" onClick={onClose}>
                    <Percent size={18} />
                    <span>Discounts</span>
                  </NavLink>
                  <NavLink to="/taxes" className="nav-link" onClick={onClose}>
                    <Scale size={18} />
                    <span>Taxes</span>
                  </NavLink>
                  <NavLink to="/staff" className="nav-link" onClick={onClose}>
                    <ShieldCheck size={18} />
                    <span>Staff</span>
                  </NavLink>
                </>
              )}
            </>
          )}

          {user.role === 'CUSTOMER' && (
            <>
              <div style={{ padding: '16px 20px 6px', fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase' }}>
                Customer Portal
              </div>
              <NavLink to="/subscriptions" className="nav-link" onClick={onClose}>
                <RotateCw size={18} />
                <span>My Subscriptions</span>
              </NavLink>
              <NavLink to="/invoices" className="nav-link" onClick={onClose}>
                <Receipt size={18} />
                <span>My Invoices</span>
              </NavLink>
              <NavLink to="/payments" className="nav-link" onClick={onClose}>
                <CreditCard size={18} />
                <span>Payment History</span>
              </NavLink>
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 18px', borderTop: '1px solid var(--standard-border)' }}>
          <button onClick={logout} className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </aside>
    </>
  );
}