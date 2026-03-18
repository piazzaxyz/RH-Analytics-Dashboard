import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, Clock, DollarSign, Award, Briefcase, Wallet, LogOut } from 'lucide-react';
import { removeToken } from '../../services/auth';
import './Sidebar.css';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/employees', icon: Users, label: 'Colaboradores' },
  { to: '/timesheets', icon: Clock, label: 'Ponto' },
  { to: '/payroll', icon: DollarSign, label: 'Folha' },
  { to: '/evaluations', icon: Award, label: 'Avaliações' },
  { to: '/positions', icon: Briefcase, label: 'Cargos' },
  { to: '/loans', icon: Wallet, label: 'Empréstimos' },
];

const Sidebar: React.FC = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    removeToken();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <LayoutDashboard size={28} />
          <span>RH Analytics</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            end={to === '/'}
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="sidebar-link logout-btn" onClick={handleLogout}>
          <LogOut size={20} />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
