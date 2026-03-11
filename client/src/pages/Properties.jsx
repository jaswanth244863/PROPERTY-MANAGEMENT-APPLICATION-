import { useEffect, useState } from 'react';
import { propertiesApi } from '../api/api';
import { FaPlus, FaEdit, FaTrash } from 'react-icons/fa';

const EMPTY_FORM = {
  name: '', address: '', city: '', state: '', zip: '',
  type: 'apartment', units: 1, rent: '', status: 'available', description: '',
};

export default function Properties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const loadProperties = () => {
    propertiesApi.getAll()
      .then(res => setProperties(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadProperties(); }, []);

  const openAdd = () => { setForm(EMPTY_FORM); setEditing(null); setError(''); setShowForm(true); };
  const openEdit = (p) => { setForm({ ...p }); setEditing(p.id); setError(''); setShowForm(true); };
  const closeForm = () => { setShowForm(false); setEditing(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        await propertiesApi.update(editing, form);
      } else {
        await propertiesApi.create(form);
      }
      loadProperties();
      closeForm();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this property?')) return;
    await propertiesApi.delete(id);
    loadProperties();
  };

  if (loading) return <div className="loading">Loading properties...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Properties</h1>
        <button className="btn btn-primary" onClick={openAdd}>
          <FaPlus /> Add Property
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={closeForm}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2>{editing ? 'Edit Property' : 'Add Property'}</h2>
            {error && <div className="form-error">{error}</div>}
            <form onSubmit={handleSubmit} className="form">
              <div className="form-row">
                <div className="form-group">
                  <label>Name *</label>
                  <input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>Type *</label>
                  <select value={form.type} onChange={e => setForm({ ...form, type: e.target.value })}>
                    <option value="apartment">Apartment</option>
                    <option value="house">House</option>
                    <option value="condo">Condo</option>
                    <option value="commercial">Commercial</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Address *</label>
                <input value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} required />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>City *</label>
                  <input value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>State *</label>
                  <input value={form.state} onChange={e => setForm({ ...form, state: e.target.value })} required />
                </div>
                <div className="form-group">
                  <label>ZIP *</label>
                  <input value={form.zip} onChange={e => setForm({ ...form, zip: e.target.value })} required />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Units</label>
                  <input type="number" min="1" value={form.units} onChange={e => setForm({ ...form, units: parseInt(e.target.value) || 1 })} />
                </div>
                <div className="form-group">
                  <label>Monthly Rent ($) *</label>
                  <input type="number" min="0" step="0.01" value={form.rent} onChange={e => setForm({ ...form, rent: parseFloat(e.target.value) || 0 })} required />
                </div>
                <div className="form-group">
                  <label>Status</label>
                  <select value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                    <option value="available">Available</option>
                    <option value="occupied">Occupied</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} rows={3} />
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeForm}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editing ? 'Save Changes' : 'Add Property'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {properties.length === 0 ? (
        <p className="empty-msg">No properties found. Add your first property!</p>
      ) : (
        <div className="cards-grid">
          {properties.map(p => (
            <div key={p.id} className="property-card">
              <div className="property-card-header">
                <span className="property-type">{p.type}</span>
                <span className={`badge badge-${p.status}`}>{p.status}</span>
              </div>
              <h3>{p.name}</h3>
              <p className="property-address">{p.address}, {p.city}, {p.state} {p.zip}</p>
              <div className="property-details">
                <span>{p.units} unit{p.units !== 1 ? 's' : ''}</span>
                <span className="property-rent">${p.rent.toLocaleString()}/mo</span>
              </div>
              {p.description && <p className="property-desc">{p.description}</p>}
              <div className="card-actions">
                <button className="btn btn-sm btn-secondary" onClick={() => openEdit(p)}>
                  <FaEdit /> Edit
                </button>
                <button className="btn btn-sm btn-danger" onClick={() => handleDelete(p.id)}>
                  <FaTrash /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
