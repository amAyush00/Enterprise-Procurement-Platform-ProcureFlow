import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Table from '../components/Table';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { Eye, FileDown, Plus, HelpCircle, Truck, ClipboardCheck } from 'lucide-react';

const PurchaseOrders = () => {
  const { hasRole } = useAuth();
  const toast = useToast();

  const [orders, setOrders] = useState([]);
  const [approvedRequests, setApprovedRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Detail Modal states
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  // Create Modal states (convert approved PR to PO)
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedPrId, setSelectedPrId] = useState('');
  const [expectedDate, setExpectedDate] = useState('');

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 10,
        status: statusFilter || undefined,
        search: search || undefined
      };
      const response = await api.get('/purchase-orders', { params });
      if (response.data.success) {
        setOrders(response.data.data.purchase_orders);
        setTotalPages(response.data.data.pages);
      }
    } catch (e) {
      toast.error('Failed to load purchase orders.');
    } finally {
      setLoading(false);
    }
  };

  const fetchApprovedRequests = async () => {
    try {
      const response = await api.get('/purchase-requests', { params: { status: 'APPROVED', limit: 100 } });
      if (response.data.success) {
        setApprovedRequests(response.data.data.requests);
      }
    } catch (e) {
      toast.error('Failed to fetch approved requisitions.');
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, statusFilter]);

  useEffect(() => {
    if (isCreateOpen) {
      fetchApprovedRequests();
    }
  }, [isCreateOpen]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchOrders();
  };

  const openGenerateModal = () => {
    setSelectedPrId('');
    setExpectedDate('');
    setIsCreateOpen(true);
  };

  const handleGenerateSubmit = async () => {
    if (!selectedPrId || !expectedDate) {
      toast.error('Approved requisition ID and expected delivery date are required.');
      return;
    }

    try {
      const response = await api.post('/purchase-orders', {
        purchase_request_id: parseInt(selectedPrId),
        expected_delivery_date: expectedDate
      });

      if (response.data.success) {
        toast.success(response.data.message || 'Generated Purchase Orders successfully.');
        setIsCreateOpen(false);
        fetchOrders();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to generate orders.');
    }
  };

  const openOrderDetail = (po) => {
    setSelectedOrder(po);
    setIsDetailOpen(true);
  };

  const handleUpdateStatus = async (newStatus) => {
    try {
      const response = await api.put(`/purchase-orders/${selectedOrder.id}/status`, {
        status: newStatus
      });

      if (response.data.success) {
        toast.success(`Order status transitioned to ${newStatus}.`);
        setIsDetailOpen(false);
        fetchOrders();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to update order status.');
    }
  };

  const handleDownloadPdf = async (po) => {
    try {
      const response = await api.get(`/reports/purchase-orders/${po.id}/pdf`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `PurchaseOrder_${po.po_number}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Purchase Order PDF downloaded.');
    } catch (e) {
      toast.error('Failed to download PO PDF.');
    }
  };

  const headers = [
    { key: 'po_number', label: 'PO Number', sortable: true },
    { key: 'vendor_name', label: 'Supplier Vendor' },
    { key: 'total_amount', label: 'Total Amount', align: 'right', render: (row) => (
      <span style={{ fontWeight: '600' }}>₹{parseFloat(row.total_amount).toFixed(2)}</span>
    )},
    { key: 'expected_delivery_date', label: 'Expected Delivery Date', render: (row) => (
      <span>{new Date(row.expected_delivery_date).toLocaleDateString()}</span>
    )},
    { key: 'actual_delivery_date', label: 'Actual Delivery', render: (row) => (
      <span>{row.actual_delivery_date ? new Date(row.actual_delivery_date).toLocaleDateString() : '-'}</span>
    )},
    { key: 'status', label: 'Status', align: 'center', render: (row) => (
      <span className={`badge badge-${row.status.toLowerCase()}`}>{row.status}</span>
    )},
    {
      key: 'actions',
      label: 'Actions',
      align: 'center',
      render: (row) => (
        <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
          <Button variant="secondary" size="sm" onClick={() => openOrderDetail(row)} icon={Eye}>
            Details
          </Button>
          <Button variant="secondary" size="sm" onClick={() => handleDownloadPdf(row)} icon={FileDown} title="Download PO PDF">
            PDF
          </Button>
        </div>
      )
    }
  ];

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Purchase Orders</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Issue purchase orders, track incoming logistics, and manage delivery confirmations.
          </span>
        </div>
        {hasRole(['Admin', 'Procurement Officer']) && (
          <Button variant="primary" onClick={openGenerateModal} icon={Plus}>
            Generate PO from Requisition
          </Button>
        )}
      </div>

      {/* Filter / Search Bar */}
      <div className="card-enterprise" style={{ padding: '12px 16px', marginBottom: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', flex: 1, minWidth: '240px', border: '1px solid var(--border)', borderRadius: '4px', overflow: 'hidden', backgroundColor: '#ffffff' }}>
            <input
              type="text"
              placeholder="Search by PO Number..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ flex: 1, padding: '6px 12px', border: 'none', outline: 'none', fontSize: '13px' }}
            />
            <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#f1f5f9', border: 'none', borderLeft: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text-secondary)' }}>
              🔎
            </button>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => {
              setPage(1);
              setStatusFilter(e.target.value);
            }}
            className="form-select"
            style={{ width: '160px', padding: '6px 10px', height: '32px' }}
          >
            <option value="">All Orders</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="ORDERED">Ordered</option>
            <option value="DELIVERED">Delivered</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </form>
      </div>

      {/* Main Table */}
      <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
        <Table
          headers={headers}
          data={orders}
          isLoading={loading}
        />

        {!loading && totalPages > 1 && (
          <div className="flex-between" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--border)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Page {page} of {totalPages}
            </span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(p - 1, 1))}
              >
                Previous
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page === totalPages}
                onClick={() => setPage(p => Math.min(p + 1, totalPages))}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      <Modal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        title={`Purchase Order Details: ${selectedOrder?.po_number}`}
        size="lg"
        footerButtons={[
          { label: 'Close', onClick: () => setIsDetailOpen(false), variant: 'secondary' }
        ]}
      >
        <div style={{ marginBottom: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Supplier Vendor:</b> {selectedOrder?.vendor_name}</p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Expected Date:</b> {selectedOrder && new Date(selectedOrder.expected_delivery_date).toLocaleDateString()}</p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Actual Delivery:</b> {selectedOrder?.actual_delivery_date ? new Date(selectedOrder.actual_delivery_date).toLocaleDateString() : 'Pending'}</p>
          </div>
          <div>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Order Status:</b> <span className={`badge badge-${selectedOrder?.status.toLowerCase()}`}>{selectedOrder?.status}</span></p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Total Cost (INR):</b> <span style={{ fontWeight: '600', color: 'var(--primary)' }}>₹{selectedOrder && parseFloat(selectedOrder.total_amount).toFixed(2)}</span></p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Origin Request:</b> {selectedOrder?.purchase_request_id ? `#PR-${selectedOrder.purchase_request_id}` : 'Direct PO'}</p>
          </div>
        </div>

        {/* PO Logistics Workflow Management (Authorized Roles Only) */}
        {hasRole(['Admin', 'Procurement Officer']) && (
          <div className="card-enterprise" style={{ padding: '12px 16px', backgroundColor: '#f1f5f9', border: '1px dashed #cbd5e1', marginBottom: '20px' }}>
            <h4 style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>Logistics Lifecycle Controls</h4>
            <div style={{ display: 'flex', gap: '10px' }}>
              {selectedOrder?.status === 'PENDING' && (
                <>
                  <Button variant="primary" size="sm" onClick={() => handleUpdateStatus('ORDERED')} icon={Truck}>
                    Mark as Sent/Ordered
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleUpdateStatus('CANCELLED')}>
                    Cancel Order
                  </Button>
                </>
              )}
              {selectedOrder?.status === 'ORDERED' && (
                <>
                  <Button variant="primary" size="sm" onClick={() => handleUpdateStatus('DELIVERED')} icon={ClipboardCheck}>
                    Confirm Delivery Receipt
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleUpdateStatus('CANCELLED')}>
                    Cancel Order
                  </Button>
                </>
              )}
              {selectedOrder?.status === 'DELIVERED' && (
                <span style={{ fontSize: '12px', color: 'var(--success)', fontWeight: '500' }}>
                  ✓ Order delivered. Stock updated in warehouse.
                </span>
              )}
              {selectedOrder?.status === 'CANCELLED' && (
                <span style={{ fontSize: '12px', color: 'var(--danger)', fontWeight: '500' }}>
                  ✕ Order cancelled. No adjustments allowed.
                </span>
              )}
            </div>
          </div>
        )}

        <h4 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>Ordered Products list</h4>
        <table className="ent-table" style={{ width: '100%', border: '1px solid var(--border)', borderRadius: '4px' }}>
          <thead>
            <tr>
              <th style={{ padding: '8px 10px', fontSize: '11px' }}>SKU</th>
              <th style={{ padding: '8px 10px', fontSize: '11px' }}>Product</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Quantity</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Price</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Total</th>
            </tr>
          </thead>
          <tbody>
            {selectedOrder?.items.map((item, idx) => (
              <tr key={idx}>
                <td style={{ padding: '8px 10px', fontSize: '12px' }}>{item.product_sku}</td>
                <td style={{ padding: '8px 10px', fontSize: '12px' }}>{item.product_name}</td>
                <td style={{ padding: '8px 10px', fontSize: '12px', textAlign: 'right' }}>{item.quantity}</td>
                <td style={{ padding: '8px 10px', fontSize: '12px', textAlign: 'right' }}>₹{parseFloat(item.unit_price).toFixed(2)}</td>
                <td style={{ padding: '8px 10px', fontSize: '12px', textAlign: 'right', fontWeight: '500' }}>₹{parseFloat(item.total_price).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Modal>

      {/* Generate PO Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Generate Vendor Purchase Orders"
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsCreateOpen(false), variant: 'secondary' },
          { label: 'Generate POs', onClick: handleGenerateSubmit, variant: 'primary', disabled: !selectedPrId || !expectedDate }
        ]}
      >
        <Input
          label="Select Approved Requisition Request"
          name="purchase_request_id"
          type="select"
          value={selectedPrId}
          onChange={(e) => setSelectedPrId(e.target.value)}
          placeholder="-- Select approved request --"
          options={approvedRequests.map(r => ({
            value: r.id,
            label: `Request #${r.id} - Submitted by ${r.employee_name} (₹${parseFloat(r.total_amount).toFixed(2)})`
          }))}
          required
        />

        <Input
          label="Expected Delivery Date"
          name="expected_delivery_date"
          type="date"
          value={expectedDate}
          onChange={(e) => setExpectedDate(e.target.value)}
          required
        />

        <div style={{ marginTop: '12px', padding: '10px 14px', backgroundColor: '#eff6ff', borderRadius: '4px', border: '1px solid #bfdbfe' }}>
          <span style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: '500', display: 'flex', gap: '6px', alignItems: 'center' }}>
            <HelpCircle size={14} /> Note: Items in the requisition will be split and grouped by vendor automatically.
          </span>
        </div>
      </Modal>
    </div>
  );
};

export default PurchaseOrders;
