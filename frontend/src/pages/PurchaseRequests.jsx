import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Table from '../components/Table';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { Plus, Check, X, Eye, Trash2 } from 'lucide-react';

const PurchaseRequests = () => {
  const { user, hasRole } = useAuth();
  const toast = useToast();

  const [requests, setRequests] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Detail Modal states
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);

  // Create Form Modal states
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [comments, setComments] = useState('');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [itemQty, setItemQty] = useState('1');
  const [localItems, setLocalItems] = useState([]); // Array of { product_id, name, sku, quantity, unit_price }

  // Review Modal states
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [reviewStatus, setReviewStatus] = useState(''); // 'APPROVED' or 'REJECTED'
  const [reviewComments, setReviewComments] = useState('');

  const fetchDropdownProducts = async () => {
    try {
      const response = await api.get('/products', { params: { limit: 100, status: 'ACTIVE' } });
      if (response.data.success) {
        setProducts(response.data.data.products);
      }
    } catch (e) {
      toast.error('Failed to load products list for requests.');
    }
  };

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 10,
        status: statusFilter || undefined
      };
      const response = await api.get('/purchase-requests', { params });
      if (response.data.success) {
        setRequests(response.data.data.requests);
        setTotalPages(response.data.data.pages);
      }
    } catch (e) {
      toast.error('Failed to load purchase requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [page, statusFilter]);

  useEffect(() => {
    if (isCreateOpen) {
      fetchDropdownProducts();
    }
  }, [isCreateOpen]);

  const openCreateModal = () => {
    setComments('');
    setSelectedProductId('');
    setItemQty('1');
    setLocalItems([]);
    setIsCreateOpen(true);
  };

  const addLocalItem = () => {
    if (!selectedProductId || !itemQty || parseInt(itemQty) <= 0) {
      toast.error('Please select a product and enter a valid quantity.');
      return;
    }

    const prod = products.find(p => p.id === parseInt(selectedProductId));
    if (!prod) return;

    // Check if item is already added locally
    if (localItems.some(item => item.product_id === prod.id)) {
      toast.error('Product already added to request list. Update its quantity instead.');
      return;
    }

    setLocalItems(prev => [
      ...prev,
      {
        product_id: prod.id,
        name: prod.name,
        sku: prod.sku,
        quantity: parseInt(itemQty),
        unit_price: prod.unit_price
      }
    ]);

    // Reset items select input
    setSelectedProductId('');
    setItemQty('1');
  };

  const removeLocalItem = (index) => {
    setLocalItems(prev => prev.filter((_, idx) => idx !== index));
  };

  const handleCreateSubmit = async () => {
    if (localItems.length === 0) {
      toast.error('Please add at least one product item to your request.');
      return;
    }

    try {
      const payload = {
        comments,
        items: localItems.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        }))
      };

      const response = await api.post('/purchase-requests', payload);
      if (response.data.success) {
        toast.success('Purchase request submitted successfully.');
        setIsCreateOpen(false);
        fetchRequests();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to submit request.');
    }
  };

  const openRequestDetail = (req) => {
    setSelectedRequest(req);
    setIsDetailOpen(true);
  };

  const openReviewModal = (status) => {
    setReviewStatus(status);
    setReviewComments('');
    setIsReviewOpen(true);
  };

  const handleReviewSubmit = async () => {
    try {
      const response = await api.post(`/purchase-requests/${selectedRequest.id}/review`, {
        status: reviewStatus,
        comments: reviewComments
      });

      if (response.data.success) {
        toast.success(`Purchase request ${reviewStatus.toLowerCase()} successfully.`);
        setIsReviewOpen(false);
        setIsDetailOpen(false);
        fetchRequests();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to review request.');
    }
  };

  const headers = [
    { key: 'id', label: 'ID', render: (row) => <span>#{row.id}</span> },
    { key: 'employee_name', label: 'Requested By' },
    { key: 'total_amount', label: 'Total Amount', align: 'right', render: (row) => (
      <span style={{ fontWeight: '500' }}>₹{parseFloat(row.total_amount).toFixed(2)}</span>
    )},
    { key: 'comments', label: 'Purpose/Comments', render: (row) => (
      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
        {row.comments || '-'}
      </span>
    )},
    { key: 'created_at', label: 'Submission Date', render: (row) => (
      <span>{new Date(row.created_at).toLocaleDateString()}</span>
    )},
    { key: 'status', label: 'Status', align: 'center', render: (row) => (
      <span className={`badge badge-${row.status.toLowerCase()}`}>{row.status}</span>
    )},
    {
      key: 'actions',
      label: 'Actions',
      align: 'center',
      render: (row) => (
        <Button variant="secondary" size="sm" onClick={() => openRequestDetail(row)} icon={Eye}>
          View Details
        </Button>
      )
    }
  ];

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Purchase Requests</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Submit, track, and review company asset requisition flows.
          </span>
        </div>
        <Button variant="primary" onClick={openCreateModal} icon={Plus}>
          Create Requisition Request
        </Button>
      </div>

      {/* Filters */}
      <div className="card-enterprise" style={{ padding: '12px 16px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-secondary)' }}>Status Filter:</span>
          <select
            value={statusFilter}
            onChange={(e) => {
              setPage(1);
              setStatusFilter(e.target.value);
            }}
            className="form-select"
            style={{ width: '160px', padding: '4px 8px', height: '28px' }}
          >
            <option value="">All Requisitions</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="CONVERTED">Converted to PO</option>
          </select>
        </div>
      </div>

      {/* Main Table */}
      <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
        <Table
          headers={headers}
          data={requests}
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
        title={`Purchase Requisition Detail: Request #${selectedRequest?.id}`}
        size="lg"
        footerButtons={
          selectedRequest?.status === 'PENDING' && hasRole(['Admin', 'Manager']) ? [
            { label: 'Reject Request', onClick: () => openReviewModal('REJECTED'), variant: 'danger' },
            { label: 'Approve Request', onClick: () => openReviewModal('APPROVED'), variant: 'primary' }
          ] : [
            { label: 'Close', onClick: () => setIsDetailOpen(false), variant: 'secondary' }
          ]
        }
      >
        <div style={{ marginBottom: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Requested By:</b> {selectedRequest?.employee_name}</p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Submission Date:</b> {selectedRequest && new Date(selectedRequest.created_at).toLocaleString()}</p>
          </div>
          <div>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Requisition Status:</b> <span className={`badge badge-${selectedRequest?.status.toLowerCase()}`}>{selectedRequest?.status}</span></p>
            <p style={{ margin: '4px 0', fontSize: '13px' }}><b>Total Value (INR):</b> <span style={{ fontWeight: '600', color: 'var(--primary)' }}>₹{selectedRequest && parseFloat(selectedRequest.total_amount).toFixed(2)}</span></p>
          </div>
        </div>

        <div style={{ margin: '12px 0 20px 0' }}>
          <p style={{ fontSize: '13px' }}><b>Requisition Comments:</b></p>
          <div style={{ padding: '8px 12px', border: '1px solid var(--border)', borderRadius: '4px', marginTop: '6px', fontSize: '12px', color: 'var(--text-secondary)', backgroundColor: '#f8fafc' }}>
            {selectedRequest?.comments || 'No comments provided.'}
          </div>
        </div>

        <h4 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>Requested Items List</h4>
        <table className="ent-table" style={{ width: '100%', border: '1px solid var(--border)', borderRadius: '4px' }}>
          <thead>
            <tr>
              <th style={{ padding: '8px 10px', fontSize: '11px' }}>SKU</th>
              <th style={{ padding: '8px 10px', fontSize: '11px' }}>Product</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Quantity</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Est. Price</th>
              <th style={{ padding: '8px 10px', fontSize: '11px', textAlign: 'right' }}>Line Total</th>
            </tr>
          </thead>
          <tbody>
            {selectedRequest?.items.map((item, idx) => (
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

      {/* Review input modal */}
      <Modal
        isOpen={isReviewOpen}
        onClose={() => setIsReviewOpen(false)}
        title={reviewStatus === 'APPROVED' ? 'Confirm Requisition Approval' : 'Confirm Requisition Rejection'}
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsReviewOpen(false), variant: 'secondary' },
          { label: reviewStatus === 'APPROVED' ? 'Approve Requisition' : 'Reject Requisition', onClick: handleReviewSubmit, variant: reviewStatus === 'APPROVED' ? 'primary' : 'danger' }
        ]}
      >
        <Input
          label="Review Notes / Feedback Comments"
          name="reviewComments"
          type="textarea"
          value={reviewComments}
          onChange={(e) => setReviewComments(e.target.value)}
          placeholder="e.g. Budget approved for department or Rejected due to redundant warehouse asset levels."
          required
        />
      </Modal>

      {/* Create Requisition Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Submit Purchase Requisition Request"
        size="lg"
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsCreateOpen(false), variant: 'secondary' },
          { label: 'Submit Requisition', onClick: handleCreateSubmit, variant: 'primary', disabled: localItems.length === 0 }
        ]}
      >
        {/* Item adder block */}
        <div className="card-enterprise" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', marginBottom: '16px' }}>
          <h4 style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-secondary)' }}>Add Product Line Item</h4>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '200px' }}>
              <label style={{ fontSize: '11px', fontWeight: '500', display: 'block', marginBottom: '4px' }}>Select Product Catalog Item</label>
              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="form-select"
                style={{ height: '32px', padding: '4px 8px' }}
              >
                <option value="">-- Select Active Item --</option>
                {products.map(p => (
                  <option key={p.id} value={p.id}>{p.name} (SKU: {p.sku} - ₹{p.unit_price})</option>
                ))}
              </select>
            </div>
            
            <div style={{ width: '90px' }}>
              <label style={{ fontSize: '11px', fontWeight: '500', display: 'block', marginBottom: '4px' }}>Quantity</label>
              <input
                type="number"
                min="1"
                value={itemQty}
                onChange={(e) => setItemQty(e.target.value)}
                className="form-input"
                style={{ height: '32px', padding: '4px 8px' }}
              />
            </div>

            <Button variant="secondary" onClick={addLocalItem} size="sm" style={{ height: '32px' }}>
              Add to List
            </Button>
          </div>
        </div>

        {/* Temporary added items list table */}
        <h4 style={{ fontSize: '13px', fontWeight: '600', marginBottom: '8px' }}>Requisition Line Items</h4>
        <div className="table-container" style={{ marginBottom: '16px' }}>
          <table className="ent-table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Product Name</th>
                <th style={{ textAlign: 'right' }}>Quantity</th>
                <th style={{ textAlign: 'right' }}>Est. Unit Price</th>
                <th style={{ textAlign: 'right' }}>Subtotal</th>
                <th style={{ textAlign: 'center' }}>Remove</th>
              </tr>
            </thead>
            <tbody>
              {localItems.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '16px', color: 'var(--text-muted)' }}>
                    No items added yet. Choose a product and click 'Add to List'.
                  </td>
                </tr>
              ) : (
                localItems.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.sku}</td>
                    <td>{item.name}</td>
                    <td style={{ textAlign: 'right' }}>{item.quantity}</td>
                    <td style={{ textAlign: 'right' }}>₹{parseFloat(item.unit_price).toFixed(2)}</td>
                    <td style={{ textAlign: 'right', fontWeight: '500' }}>₹{parseFloat(item.unit_price * item.quantity).toFixed(2)}</td>
                    <td style={{ textAlign: 'center' }}>
                      <button 
                        onClick={() => removeLocalItem(idx)}
                        style={{ border: 'none', background: 'none', color: 'var(--danger)', cursor: 'pointer' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Input
          label="Business Reason Comments / Requisition Purpose"
          name="comments"
          type="textarea"
          value={comments}
          onChange={(e) => setComments(e.target.value)}
          placeholder="Explain the corporate operational necessity of this purchase requisition..."
          required
        />
      </Modal>
    </div>
  );
};

export default PurchaseRequests;
