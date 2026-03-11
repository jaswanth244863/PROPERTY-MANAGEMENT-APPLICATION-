import { useEffect, useState } from 'react';
import { dashboardApi } from '../api/api';
import { FaBuilding, FaUsers, FaFileContract, FaDollarSign } from 'react-icons/fa';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.getStats()
      .then(res => setStats(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!stats) return <div className="error">Failed to load dashboard.</div>;

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card stat-blue">
          <div className="stat-icon"><FaBuilding /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.totalProperties}</div>
            <div className="stat-label">Total Properties</div>
          </div>
        </div>
        <div className="stat-card stat-green">
          <div className="stat-icon"><FaBuilding /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.availableProperties}</div>
            <div className="stat-label">Available</div>
          </div>
        </div>
        <div className="stat-card stat-orange">
          <div className="stat-icon"><FaBuilding /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.occupiedProperties}</div>
            <div className="stat-label">Occupied</div>
          </div>
        </div>
        <div className="stat-card stat-purple">
          <div className="stat-icon"><FaUsers /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.totalTenants}</div>
            <div className="stat-label">Tenants</div>
          </div>
        </div>
        <div className="stat-card stat-teal">
          <div className="stat-icon"><FaFileContract /></div>
          <div className="stat-info">
            <div className="stat-value">{stats.activeLeases}</div>
            <div className="stat-label">Active Leases</div>
          </div>
        </div>
        <div className="stat-card stat-emerald">
          <div className="stat-icon"><FaDollarSign /></div>
          <div className="stat-info">
            <div className="stat-value">${stats.monthlyRevenue.toLocaleString()}</div>
            <div className="stat-label">Monthly Revenue</div>
          </div>
        </div>
      </div>

      <div className="section">
        <h2 className="section-title">Recent Payments</h2>
        {stats.recentPayments.length === 0 ? (
          <p className="empty-msg">No payments recorded yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Tenant</th>
                <th>Property</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {stats.recentPayments.map(p => (
                <tr key={p.id}>
                  <td>{p.first_name} {p.last_name}</td>
                  <td>{p.property_name}</td>
                  <td>${p.amount.toLocaleString()}</td>
                  <td>{p.payment_date}</td>
                  <td><span className={`badge badge-${p.status}`}>{p.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
