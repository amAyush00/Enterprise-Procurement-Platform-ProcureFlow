import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Table from '../components/Table';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { Search, FileSpreadsheet, Sliders, RotateCw, History } from 'lucide-react';

const Inventory = () => {
  const { hasRole } = useAuth();
  const toast = useToast();

  // Tab management: 'levels' vs 'ledger'
  const [activeTab, setActiveTab] = useState('levels');

  // Levels tab data
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [lowStockFilter, setLowStockFilter] = useState(false);
  const [sort, setSort] = useState({ key: 'product_name', order: 'asc' });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // Ledger tab data
  const [ledger, setLedger] = useState([]);
  const [ledgerLoading, setLedgerLoading] = useState(false);
  const [ledgerPage, setLedgerPage] = useState(1);
  const [ledgerTotalPages, setLedgerTotalPages] = useState(1);

  // Adjustment form states
  const [isAdjustOpen, setIsAdjustOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [adjustForm, setAdjustForm] = useState({
    quantity: '',
    notes: ''
  });

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 10,
        sort_by: sort.key,
        sort_order: sort.order,
        search: search || undefined,
        low_stock: lowStockFilter ? 'true' : 'false'
      };

      const response = await api.get('/inventory', { params });
      if (response.data && response.data.success) {
        setInventory(response.data.data.inventory);
        setTotalPages(response.data.data.pages);
        setTotalItems(response.data.data.total);
      }
    } catch (e) {
      toast.error('Failed to load inventory levels.');
    } finally {
      setLoading(false);
    }
  };

  const fetchLedger = async () => {
    try {
      setLedgerLoading(true);
      const params = {
        page: ledgerPage,
        limit: 15
      };

      const response = await api.get('/inventory/transactions', { params });
      if (response.data && response.data.success) {
        setLedger(response.data.data.transactions);
        setLedgerTotalPages(response.data.data.pages);
      }
    } catch (e) {
      toast.error('Failed to load transaction ledger logs.');
    } finally {
      setLedgerLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'levels') {
      fetchInventory();
    } else {
      fetchLedger();
    }
  }, [activeTab, page, sort, lowStockFilter, ledgerPage]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchInventory();
  };

  const handleSort = (key, order) => {
    setSort({ key, order });
  };

  const openAdjustModal = (item) => {
    setSelectedItem(item);
    setAdjustForm({
      quantity: '',
      notes: ''
    });
    setIsAdjustOpen(true);
  };

  const handleAdjustSubmit = async () => {
    if (!adjustForm.quantity || !adjustForm.notes) {
      toast.error('Deduction/addition quantity and notes are required.');
      return;
    }

    const qty = parseInt(adjustForm.quantity);
    if (isNaN(qty) || qty === 0) {
      toast.error('Please enter a non-zero integer adjustment value.');
      return;
    }

    try {
      const response = await api.post('/inventory/adjust', {
        product_id: selectedItem.product_id,
        quantity: qty,
        notes: adjustForm.notes
      });

      if (response.data.success) {
        toast.success('Inventory stock level adjusted.');
        setIsAdjustOpen(false);
        fetchInventory();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to adjust stock level.');
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await api.get('/reports/inventory/excel', {
        params: { low_stock: lowStockFilter ? 'true' : 'false' },
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Inventory_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Excel report downloaded.');
    } catch (e) {
      toast.error('Failed to download Excel report.');
    }
  };

  const levelHeaders = [
    { key: 'product_sku', label: 'SKU', sortable: true },
    { key: 'product_name', label: 'Product Name', sortable: true },
    { key: 'product_category', label: 'Category' },
    { key: 'current_stock', label: 'Current Stock', sortable: true, align: 'right', render: (row) => (
      <span style={{ fontWeight: '600', color: row.current_stock <= row.reorder_level ? 'var(--danger)' : 'inherit' }}>
        {row.current_stock}
      </span>
    )},
    { key: 'incoming_stock', label: 'Incoming Orders', align: 'right', render: (row) => (
      <span style={{ color: row.incoming_stock > 0 ? 'var(--primary)' : 'inherit' }}>
        +{row.incoming_stock}
      </span>
    )},
    { key: 'outgoing_stock', label: 'Allocated', align: 'right' },
    { key: 'reorder_level', label: 'Reorder Level', align: 'right' },
    { key: 'unit_price', label: 'Unit Price', align: 'right', render: (row) => (
      <span>₹{parseFloat(row.unit_price).toFixed(2)}</span>
    )},
    { key: 'inventory_value', label: 'Inventory Value', sortable: true, align: 'right', render: (row) => (
      <span style={{ fontWeight: '500' }}>₹{parseFloat(row.inventory_value).toFixed(2)}</span>
    )},
    {
      key: 'actions',
      label: 'Actions',
      align: 'center',
      render: (row) => (
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          {hasRole(['Admin', 'Procurement Officer']) && (
            <Button variant="secondary" size="sm" onClick={() => openAdjustModal(row)} icon={Sliders}>
              Adjust Stock
            </Button>
          )}
        </div>
      )
    }
  ];

  const ledgerHeaders = [
    { key: 'transaction_date', label: 'Timestamp', render: (row) => (
      <span>{new Date(row.transaction_date).toLocaleString()}</span>
    )},
    { key: 'product_sku', label: 'SKU' },
    { key: 'product_name', label: 'Product Name' },
    { key: 'transaction_type', label: 'Type', align: 'center', render: (row) => (
      <span className={`badge badge-${row.transaction_type.toLowerCase()}`}>
        {row.transaction_type}
      </span>
    )},
    { key: 'quantity', label: 'Quantity Change', align: 'right', render: (row) => (
      <span style={{ fontWeight: '600', color: row.quantity > 0 ? 'var(--success)' : 'var(--danger)' }}>
        {row.quantity > 0 ? `+${row.quantity}` : row.quantity}
      </span>
    )},
    { key: 'reference_id', label: 'Reference ID', align: 'center', render: (row) => (
      <span>{row.reference_id ? `#PO-${row.reference_id}` : '-'}</span>
    )},
    { key: 'notes', label: 'Notes/Comments' }
  ];

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Inventory Warehouse Management</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Monitor real-time warehouse stock, incoming shipments, allocations, and transaction ledgers.
          </span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button
            variant="secondary"
            onClick={() => setActiveTab(activeTab === 'levels' ? 'ledger' : 'levels')}
            icon={activeTab === 'levels' ? History : RotateCw}
          >
            {activeTab === 'levels' ? 'View Ledger Audit Logs' : 'View Current Stock Levels'}
          </Button>
          {activeTab === 'levels' && (
            <Button variant="secondary" onClick={handleExportExcel} icon={FileSpreadsheet}>
              Export Excel
            </Button>
          )}
        </div>
      </div>

      {activeTab === 'levels' ? (
        <>
          {/* Filtering Panel */}
          <div className="card-enterprise" style={{ padding: '12px 16px', marginBottom: '16px' }}>
            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', flex: 1, minWidth: '240px', border: '1px solid var(--border)', borderRadius: '4px', overflow: 'hidden', backgroundColor: '#ffffff' }}>
                <input
                  type="text"
                  placeholder="Search stock by SKU or name..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  style={{ flex: 1, padding: '6px 12px', border: 'none', outline: 'none', fontSize: '13px' }}
                />
                <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#f1f5f9', border: 'none', borderLeft: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                  <Search size={14} />
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  id="lowStockCheck"
                  checked={lowStockFilter}
                  onChange={(e) => {
                    setPage(1);
                    setLowStockFilter(e.target.checked);
                  }}
                  style={{ cursor: 'pointer' }}
                />
                <label htmlFor="lowStockCheck" style={{ fontSize: '13px', fontWeight: '500', cursor: 'pointer', color: 'var(--danger)' }}>
                  ⚠️ Only Show Low Stock Warnings
                </label>
              </div>
            </form>
          </div>

          {/* Levels Table */}
          <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
            <Table
              headers={levelHeaders}
              data={inventory}
              isLoading={loading}
              onSort={handleSort}
              currentSort={sort}
            />

            {!loading && totalPages > 1 && (
              <div className="flex-between" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--border)' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Showing {inventory.length} of {totalItems} items
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
        </>
      ) : (
        /* Ledger tab layout */
        <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
          <Table
            headers={ledgerHeaders}
            data={ledger}
            isLoading={ledgerLoading}
          />

          {!ledgerLoading && ledgerTotalPages > 1 && (
            <div className="flex-between" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--border)' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Page {ledgerPage} of {ledgerTotalPages}
              </span>
              <div style={{ display: 'flex', gap: '6px' }}>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={ledgerPage === 1}
                  onClick={() => setLedgerPage(p => Math.max(p - 1, 1))}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={ledgerPage === ledgerTotalPages}
                  onClick={() => setLedgerPage(p => Math.min(p + 1, ledgerTotalPages))}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Adjust stock modal */}
      <Modal
        isOpen={isAdjustOpen}
        onClose={() => setIsAdjustOpen(false)}
        title={`Adjust Stock: ${selectedItem?.product_name}`}
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsAdjustOpen(false), variant: 'secondary' },
          { label: 'Confirm Adjustment', onClick: handleAdjustSubmit, variant: 'primary' }
        ]}
      >
        <div style={{ marginBottom: '16px', fontSize: '13px', color: 'var(--text-secondary)' }}>
          Current stock level: <b>{selectedItem?.current_stock}</b> items.
        </div>
        
        <Input
          label="Adjustment Value (Positive to Add, Negative to Deduct)"
          name="quantity"
          type="number"
          value={adjustForm.quantity}
          onChange={(e) => setAdjustForm(prev => ({ ...prev, quantity: e.target.value }))}
          placeholder="e.g. 15 or -10"
          required
        />

        <Input
          label="Adjustment Reason Notes"
          name="notes"
          type="textarea"
          value={adjustForm.notes}
          onChange={(e) => setAdjustForm(prev => ({ ...prev, notes: e.target.value }))}
          placeholder="e.g. Damaged inventory deduction or manual count correction."
          required
        />
      </Modal>
    </div>
  );
};

export default Inventory;
