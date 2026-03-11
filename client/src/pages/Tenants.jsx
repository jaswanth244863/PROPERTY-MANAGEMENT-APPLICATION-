import { useEffect, useState } from 'react';
import { tenantsApi } from '../api/api';
import { FaPlus, FaEdit, FaTrash, FaUser } from 'react-icons/fa';

const EMPTY_FORM = { first_name: '', last_name: '', email: '', phone: '' };

export default function Tenants() {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');

  const load = () => {
    tenantsApi.getAll()
      .then(res => setTenants(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const openAdd = () => { setForm(EMPTY_FORM); setEditing(null); setError(''); setShowForm(true); };
  const openEdit = (t) => { setForm({ ...t }); setEditing(t.id); setError(''); setShowForm(true); };
  const closeForm = () => { setShowForm(false); setEditing(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        await tenantsApi.update(editing, form);
      } else {
        await tenantsApi.create(form);
      }
      load();
      closeForm();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this tenant?')) return;
    await tenantsApi.delete(id);
    load();
  };

  const filtered = tenants.filter(t =>
    `${t.first_name} ${t.last_name} ${t.email}`.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <div className="loading">Loading tenants...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Tenants</h1>
        <button className="btn btn-primary" onClick={openAdd}>
          <FaPlus /> Add Tenant
        </button>
      </div>

      <input
        className="search-input"
        placeholder="Search tenants..."
        value={search}
        onChange={e => setSearch(e.target.value)}
      />

      {showForm && (
        <div className="modal-overlay" onClick={closeForm}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{editing ? 'Edit Tenant' : 'Add Tenant'}</h2>
            {error && <div className="form-error">{error}</div>}
            <form onSubmit={handleSubmit} className="form">
              <div className="form-row">
                <div className="form-group">
                  <label>First Name *</label>
                  <input value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Last Name *</label>
                  <input value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} required />
                </div>
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeForm}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editing ? 'Save Changes' : 'Add Tenant'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {filtered.length === 0 ? (
        <p className="empty-msg">{tenants.length === 0 ? 'No tenants yet. Add your first tenant!' : 'No tenants match your search.'}</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(t => (
              <tr key={t.id}>
                <td>
                  <span className="tenant-avatar"><FaUser /></span>
                  {t.first_name} {t.last_name}
                </td>
                <td>{t.email}</td>
                <td>{t.phone || '—'}</td>
                <td>
                  <div className="row-actions">
                    <button className="btn btn-sm btn-secondary" onClick={() => openEdit(t)}>
                      <FaEdit />
                    </button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(t.id)}>
                      <FaTrash />
                    </button>
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
