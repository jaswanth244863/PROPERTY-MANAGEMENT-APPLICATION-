import { NavLink } from 'react-router-dom';
import { FaHome, FaBuilding, FaUsers, FaFileContract, FaCreditCard } from 'react-icons/fa';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <FaBuilding />
        <span>PropManage</span>
      </div>
      <ul className="navbar-links">
        <li>
          <NavLink to="/" end>
            <FaHome /> Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink to="/properties">
            <FaBuilding /> Properties
          </NavLink>
        </li>
        <li>
          <NavLink to="/tenants">
            <FaUsers /> Tenants
          </NavLink>
        </li>
        <li>
          <NavLink to="/leases">
            <FaFileContract /> Leases
          </NavLink>
        </li>
        <li>
          <NavLink to="/payments">
            <FaCreditCard /> Payments
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}
