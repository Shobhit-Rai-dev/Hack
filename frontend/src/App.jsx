import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Products from './pages/Products';
import Plans from './pages/Plans';
import Quotations from './pages/Quotations.jsx';
import Subscriptions from './pages/Subscriptions';
import Invoices from './pages/Invoices';
import Payments from './pages/Payments';
import QuotationTemplates from './pages/QuotationTemplates';
import Discounts from './pages/Discounts';
import Taxes from './pages/Taxes';
import StaffManagement from './pages/StaffManagement';
import { Menu } from 'lucide-react';

function ProtectedLayout() {
  const { user } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="app-container">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="main-content">
        <header className="topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button 
              onClick={() => setSidebarOpen(true)}
              className="no-print"
              style={{
                display: 'inline-flex',
                background: 'none',
                border: '1px solid var(--standard-border)',
                borderRadius: 4,
                padding: 6,
                cursor: 'pointer',
                color: 'var(--text-primary)'
              }}
              aria-label="Open navigation menu"
            >
              <Menu size={18} />
            </button>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              SubscriptIQ &bull; <strong style={{ color: 'var(--primary-accent)' }}>{user.role}</strong>
            </div>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
            <strong>{user.full_name}</strong>
          </div>
        </header>
        <main className="page-body">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/products" element={<Products />} />
            <Route path="/plans" element={<Plans />} />
            <Route path="/quotations" element={<Quotations />} />
            <Route path="/quotation-templates" element={<QuotationTemplates />} />
            <Route path="/subscriptions" element={<Subscriptions />} />
            <Route path="/invoices" element={<Invoices />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/discounts" element={<Discounts />} />
            <Route path="/taxes" element={<Taxes />} />
            <Route path="/staff" element={<StaffManagement />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}