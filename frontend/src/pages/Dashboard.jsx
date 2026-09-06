import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import StatCard from '../components/StatCard';
import Table from '../components/Table';
import {
  Users,
  Package,
  Warehouse,
  FileSpreadsheet,
  FileCheck,
  AlertTriangle,
  IndianRupee,
  TrendingUp,
  FileDown
} from 'lucide-react';
import Button from '../components/Button';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState(null);
  const toast = useToast();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/analytics/summary');
      if (response.data && response.data.success) {
        setKpis(response.data.data);
      }
    } catch (e) {
      toast.error('Failed to load dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleDownloadSummary = async () => {
    try {
      const response = await api.get('/reports/procurement/pdf', {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Procurement_Summary_Report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Procurement report downloaded successfully.');
    } catch (e) {
      toast.error('Failed to download PDF summary report.');
    }
  };

  const activityHeaders = [
    { key: 'type', label: 'Activity Type', render: (row) => (
      <span className={`badge badge-${row.type.toLowerCase() === 'purchase_request' ? 'converted' : 'active'}`}>
        {row.type.replace('_', ' ')}
      </span>
    )},
    { key: 'description', label: 'Description' },
    { key: 'timestamp', label: 'Date/Time', render: (row) => (
      <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
        {new Date(row.timestamp).toLocaleString()}
      </span>
    )}
  ];

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Dashboard</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Overview of enterprise procurement operations and asset status.
          </span>
        </div>
        <Button variant="secondary" onClick={handleDownloadSummary} icon={FileDown}>
          Download Corporate PDF Report
        </Button>
      </div>

      {/* Stats KPI Grid */}
      <div className="stat-grid">
        <StatCard
          title="Total Vendors"
          value={kpis ? `${kpis.active_vendors} / ${kpis.total_vendors}` : '0'}
          icon={Users}
          description="Active vs Total suppliers registered"
          loading={loading}
        />
        <StatCard
          title="Total Products"
          value={kpis ? kpis.total_products : '0'}
          icon={Package}
          description="Unique items in catalog"
          loading={loading}
        />
        <StatCard
          title="Inventory Assets Value"
          value={kpis ? `₹${kpis.inventory_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
          icon={Warehouse}
          description="Asset value stored in warehouse"
          loading={loading}
        />
        <StatCard
          title="Monthly Procurement Spend"
          value={kpis ? `₹${kpis.monthly_spending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
          icon={IndianRupee}
          description="Total PO spend this month"
          loading={loading}
        />
      </div>

      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        <StatCard
          title="Pending Purchase Requests"
          value={kpis ? kpis.pending_purchase_requests : '0'}
          icon={FileSpreadsheet}
          description="Requests waiting manager approval"
          loading={loading}
        />
        <StatCard
          title="Pending Purchase Orders"
          value={kpis ? kpis.pending_purchase_orders : '0'}
          icon={FileCheck}
          description="Open orders waiting delivery"
          loading={loading}
        />
        <StatCard
          title="Low Stock Alerts"
          value={kpis ? kpis.low_stock_alerts : '0'}
          icon={AlertTriangle}
          description="Products below reorder limits"
          loading={loading}
          style={{ borderLeft: '4px solid var(--danger)' }}
        />
      </div>

      {/* Recent Activities Section */}
      <div className="card-enterprise">
        <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
          Recent Operations Log
        </h3>
        <Table
          headers={activityHeaders}
          data={kpis ? kpis.recent_activities : []}
          isLoading={loading}
          emptyMessage="No recent operations recorded."
        />
      </div>
    </div>
  );
};

export default Dashboard;
