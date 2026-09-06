import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { FileDown, RefreshCw } from 'lucide-react';
import Button from '../components/Button';

// Enterprise Blue/Slate Palette
const COLORS = ['#2563EB', '#3B82F6', '#1E3A8A', '#60A5FA', '#93C5FD', '#1E293B', '#475569'];

const Analytics = () => {
  const toast = useToast();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  const fetchChartsData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/analytics/charts');
      if (response.data.success) {
        setData(response.data.data);
      }
    } catch (e) {
      toast.error('Failed to load analytics charts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChartsData();
  }, []);

  const handleExportSummary = async () => {
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
      toast.success('Procurement summary PDF downloaded.');
    } catch (e) {
      toast.error('Failed to download PDF summary report.');
    }
  };

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Analytics & Requisitions Reporting</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Key Performance Indicators (KPIs), vendor delivery assessments, and budget spend trends.
          </span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button variant="secondary" onClick={fetchChartsData} icon={RefreshCw} disabled={loading}>
            Refresh
          </Button>
          <Button variant="primary" onClick={handleExportSummary} icon={FileDown}>
            Download PDF Summary Report
          </Button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: 'var(--text-muted)' }}>
          Loading charts data...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '20px' }}>
          
          {/* Spend Trend */}
          <div className="card-enterprise">
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
              Monthly Procurement Spend Trend (INR)
            </h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <LineChart data={data?.monthly_spend_trend}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="month" stroke="#475569" fontSize={11} />
                  <YAxis stroke="#475569" fontSize={11} tickFormatter={(val) => `₹${val}`} />
                  <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Amount']} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="amount" stroke="#2563EB" strokeWidth={2} activeDot={{ r: 6 }} name="Spend Amount" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Vendor performance */}
          <div className="card-enterprise">
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
              Top 5 Vendors by Spend & Rating
            </h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={data?.vendor_performance}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="name" stroke="#475569" fontSize={11} />
                  <YAxis stroke="#475569" fontSize={11} tickFormatter={(val) => `₹${val}`} />
                  <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Total Spend']} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="spend" fill="#3B82F6" name="Total Spend Amount" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Inventory value by category */}
          <div className="card-enterprise">
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
              Warehouse Stock Value by Category (INR)
            </h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={data?.inventory_by_category} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E5E7EB" />
                  <XAxis type="number" stroke="#475569" fontSize={11} tickFormatter={(val) => `₹${val}`} />
                  <YAxis dataKey="name" type="category" stroke="#475569" fontSize={11} width={120} />
                  <Tooltip formatter={(value) => [`₹${value.toLocaleString()}`, 'Stock Value']} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="value" fill="#1E3A8A" name="Stock Value" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Purchase Order Status */}
          <div className="card-enterprise">
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
              Purchase Order Status Split
            </h3>
            <div style={{ width: '100%', height: 260, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: '60%', height: '100%' }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={data?.purchase_order_status_split}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="count"
                      nameKey="status"
                    >
                      {data?.purchase_order_status_split.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [value, 'Orders Count']} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Top Products */}
          <div className="card-enterprise" style={{ gridColumn: 'span 2' }}>
            <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '14px', color: 'var(--text-primary)' }}>
              Top Purchased Catalog Products (Quantity Delivered)
            </h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer>
                <BarChart data={data?.top_purchased_products}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                  <XAxis dataKey="name" stroke="#475569" fontSize={11} />
                  <YAxis stroke="#475569" fontSize={11} />
                  <Tooltip formatter={(value) => [value, 'Quantity Received']} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="quantity" fill="#2563EB" name="Quantity Delivered" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      )}
    </div>
  );
};

export default Analytics;
