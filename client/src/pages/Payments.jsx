import { useEffect, useState } from 'react';
import { paymentsApi, leasesApi } from '../api/api';
import { FaPlus } from 'react-icons/fa';

const EMPTY_FORM = {
  lease_id: '', amount: '', payment_date: new Date().toISOString().split('T')[0],
  payment_method: 'bank_transfer', status: 'paid', notes: '',
};

export default function Payments() {
  const [payments, setPayments] = useState([]);
  const [leases, setLeases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = () => {
    Promise.all([paymentsApi.getAll(), leasesApi.getAll()])
      .then(([p, l]) => { setPayments(p.data); setLeases(l.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm(EMPTY_FORM); setError(''); setShowForm(true); };
  const closeForm = () => setShowForm(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await paymentsApi.create(form);
      load();
      closeForm();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  const totalPaid = payments.filter(p => p.status === 'paid').reduce((s, p) => s + p.amount, 0);

  if (loading) return <div className="loading">Loading payments...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Payments</h1>
        <button className="btn btn-primary" onClick={openAdd}>
          <FaPlus /> Record Payment
        </button>
      </div>

      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-card stat-emerald">
          <div className="stat-info">
            <div className="stat-value">${totalPaid.toLocaleString()}</div>
            <div className="stat-label">Total Collected</div>
          </div>
        </div>
        <div className="stat-card stat-blue">
          <div className="stat-info">
            <div className="stat-value">{payments.length}</div>
            <div className="stat-label">Total Payments</div>
          </div>
        </div>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={closeForm}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>Record Payment</h2>
            {error && <div className="form-error">{error}</div>}
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label>Lease *</label>
                <select value={form.lease_id} onChange={e => setForm({ ...form, lease_id: e.target.value })} required>
                  <option value="">-- Select Lease --</option>
                  {leases.filter(l => l.status === 'active').map(l => (
                    <option key={l.id} value={l.id}>
                      {l.first_name} {l.last_name} – {l.property_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Amount ($) *</label>
                  <input type="number" min="0" step="0.01" value={form.amount} onChange={e => setForm({ ...form, amount: parseFloat(e.target.value) || 0 })} required />
                </div>
                <div className="form-group">
                  <label>Payment Date *</label>
                  <input type="date" value={form.payment_date} onChange={e => setForm({ ...form, payment_date: e.target.value })} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Method</label>
                  <select value={form.payment_method} onChange={e => setForm({ ...form, payment_method: e.target.value })}>
                    <option value="bank_transfer">Bank Transfer</option>
                    <option value="cash">Cash</option>
                    <option value="check">Check</option>
                    <option value="credit_card">Credit Card</option>
                    <option value="online">Online</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                    <option value="paid">Paid</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows={2} />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeForm}>Cancel</button>
                <button type="submit" className="btn btn-primary">Record Payment</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {payments.length === 0 ? (
        <p className="empty-msg">No payments recorded yet.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Tenant</th>
              <th>Property</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Method</th>
              <th>Status</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {payments.map(p => (
              <tr key={p.id}>
                <td>{p.first_name} {p.last_name}</td>
                <td>{p.property_name}</td>
                <td>${p.amount.toLocaleString()}</td>
                <td>{p.payment_date}</td>
                <td>{p.payment_method.replace('_', ' ')}</td>
                <td><span className={`badge badge-${p.status}`}>{p.status}</span></td>
                <td>{p.notes || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
