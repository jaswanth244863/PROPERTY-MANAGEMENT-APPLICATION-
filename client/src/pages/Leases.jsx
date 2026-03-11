import { useEffect, useState } from 'react';
import { leasesApi, propertiesApi, tenantsApi } from '../api/api';
import { FaPlus, FaEdit, FaTrash } from 'react-icons/fa';

const EMPTY_FORM = {
  property_id: '', tenant_id: '', start_date: '', end_date: '',
  monthly_rent: '', deposit: '', status: 'active',
};

export default function Leases() {
  const [leases, setLeases] = useState([]);
  const [properties, setProperties] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = () => {
    Promise.all([leasesApi.getAll(), propertiesApi.getAll(), tenantsApi.getAll()])
      .then(([l, p, t]) => { setLeases(l.data); setProperties(p.data); setTenants(t.data); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm(EMPTY_FORM); setEditing(null); setError(''); setShowForm(true); };
  const openEdit = (l) => {
    setForm({
      property_id: l.property_id, tenant_id: l.tenant_id,
      start_date: l.start_date, end_date: l.end_date,
      monthly_rent: l.monthly_rent, deposit: l.deposit, status: l.status,
    });
    setEditing(l.id);
    setError('');
    setShowForm(true);
  };
  const closeForm = () => { setShowForm(false); setEditing(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        await leasesApi.update(editing, form);
      } else {
        await leasesApi.create(form);
      }
      load();
      closeForm();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this lease?')) return;
    await leasesApi.delete(id);
    load();
  };

  if (loading) return <div className="loading">Loading leases...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Leases</h1>
        <button className="btn btn-primary" onClick={openAdd}>
          <FaPlus /> New Lease
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={closeForm}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{editing ? 'Edit Lease' : 'New Lease'}</h2>
            {error && <div className="form-error">{error}</div>}
            <form onSubmit={handleSubmit} className="form">
              <div className="form-row">
                <div className="form-group">
                  <label>Property *</label>
                  <select value={form.property_id} onChange={e => setForm({ ...form, property_id: e.target.value })} required>
                    <option value="">-- Select Property --</option>
                    {properties.map(p => (
                      <option key={p.id} value={p.id}>{p.name} ({p.address})</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Tenant *</label>
                  <select value={form.tenant_id} onChange={e => setForm({ ...form, tenant_id: e.target.value })} required>
                    <option value="">-- Select Tenant --</option>
                    {tenants.map(t => (
                      <option key={t.id} value={t.id}>{t.first_name} {t.last_name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date *</label>
                  <input type="date" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>End Date *</label>
                  <input type="date" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Monthly Rent ($) *</label>
                  <input type="number" min="0" step="0.01" value={form.monthly_rent} onChange={e => setForm({ ...form, monthly_rent: parseFloat(e.target.value) || 0 })} required />
                </div>
                <div className="form-group">
                  <label>Security Deposit ($)</label>
                  <input type="number" min="0" step="0.01" value={form.deposit} onChange={e => setForm({ ...form, deposit: parseFloat(e.target.value) || 0 })} />
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                    <option value="active">Active</option>
                    <option value="expired">Expired</option>
                    <option value="terminated">Terminated</option>
                  </select>
                </div>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeForm}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editing ? 'Save Changes' : 'Create Lease'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {leases.length === 0 ? (
        <p className="empty-msg">No leases found. Create your first lease!</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Property</th>
              <th>Tenant</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Monthly Rent</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {leases.map(l => (
              <tr key={l.id}>
                <td>{l.property_name}</td>
                <td>{l.first_name} {l.last_name}</td>
                <td>{l.start_date}</td>
                <td>{l.end_date}</td>
                <td>${parseFloat(l.monthly_rent).toLocaleString()}/mo</td>
                <td><span className={`badge badge-${l.status}`}>{l.status}</span></td>
                <td>
                  <div className="row-actions">
                    <button className="btn btn-sm btn-secondary" onClick={() => openEdit(l)}><FaEdit /></button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(l.id)}><FaTrash /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
