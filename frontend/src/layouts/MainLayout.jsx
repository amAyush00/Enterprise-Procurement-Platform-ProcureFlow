import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  LayoutDashboard,
  Users,
  Package,
  Warehouse,
  FileSpreadsheet,
  FileCheck,
  BarChart3,
  LogOut,
  User
} from 'lucide-react';
import './MainLayout.css';

const MainLayout = ({ children }) => {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Define sidebar links and their role requirements
  const menuItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      roles: ['Admin', 'Procurement Officer', 'Manager', 'Employee']
    },
    {
      path: '/vendors',
      label: 'Vendors',
      icon: Users,
      roles: ['Admin', 'Procurement Officer', 'Manager']
    },
    {
      path: '/products',
      label: 'Products',
      icon: Package,
      roles: ['Admin', 'Procurement Officer', 'Manager', 'Employee']
    },
    {
      path: '/inventory',
      label: 'Inventory',
      icon: Warehouse,
      roles: ['Admin', 'Procurement Officer', 'Manager']
    },
    {
      path: '/purchase-requests',
      label: 'Purchase Requests',
      icon: FileSpreadsheet,
      roles: ['Admin', 'Manager', 'Employee']
    },
    {
      path: '/purchase-orders',
      label: 'Purchase Orders',
      icon: FileCheck,
      roles: ['Admin', 'Procurement Officer', 'Manager']
    },
    {
      path: '/analytics',
      label: 'Analytics',
      icon: BarChart3,
      roles: ['Admin', 'Manager']
    }
  ];

  // Helper to map pathname to clean breadcrumbs
  const getBreadcrumbs = () => {
    const path = location.pathname;
    if (path === '/dashboard') return ['Dashboard'];
    
    const parts = path.split('/').filter(Boolean);
    return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1).replace('-', ' '));
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <div className="app-container">
      {/* Sidebar navigation */}
      <aside className="app-sidebar">
        <div className="sidebar-logo">
          <h3>ProcureFlow</h3>
          <span>Enterprise Portal</span>
        </div>
        
        <nav className="sidebar-nav">
          {menuItems.map((item) => {
            // Check if user role matches requirements
            if (!hasRole(item.roles)) return null;
            const Icon = item.icon;
            
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </aside>

      {/* Main viewport */}
      <div className="app-viewport">
        {/* Top Header */}
        <header className="app-header">
          <div className="header-breadcrumbs">
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={idx}>
                {idx > 0 && <span className="crumb-separator">/</span>}
                <span className={`crumb-item ${idx === breadcrumbs.length - 1 ? 'active' : ''}`}>
                  {crumb}
                </span>
              </React.Fragment>
            ))}
          </div>

          <div className="header-profile">
            <div className="profile-info">
              <span className="profile-name">
                {user?.first_name} {user?.last_name}
              </span>
              <span className={`badge badge-converted`}>
                {user?.role_name}
              </span>
            </div>
            <button className="btn-logout" onClick={handleLogout} title="Log Out">
              <LogOut size={16} />
            </button>
          </div>
        </header>

        {/* Content body */}
        <main className="app-main">
          <div className="container-max">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
