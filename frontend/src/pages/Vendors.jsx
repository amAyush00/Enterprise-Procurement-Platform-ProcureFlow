import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Table from '../components/Table';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { Plus, Search, FileSpreadsheet, Edit3, Trash2 } from 'lucide-react';

const Vendors = () => {
  const { hasRole } = useAuth();
  const toast = useToast();
  
  // Data loading states
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Table operations states
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sort, setSort] = useState({ key: 'name', order: 'asc' });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalVendors, setTotalVendors] = useState(0);

  // Form states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [vendorId, setVendorId] = useState(null);
  const [form, setForm] = useState({
    name: '',
    company_name: '',
    gst_number: '',
    email: '',
    phone: '',
    address: '',
    rating: 5.0,
    status: 'ACTIVE'
  });

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState(null);

  const fetchVendors = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 10,
        sort_by: sort.key,
        sort_order: sort.order,
        search: search || undefined,
        status: statusFilter || undefined
      };
      
      const response = await api.get('/vendors', { params });
      if (response.data && response.data.success) {
        setVendors(response.data.data.vendors);
        setTotalPages(response.data.data.pages);
        setTotalVendors(response.data.data.total);
      }
    } catch (e) {
      toast.error('Failed to load vendors.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, [page, sort, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchVendors();
  };

  const handleSort = (key, order) => {
    setSort({ key, order });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const openCreateModal = () => {
    setIsEditing(false);
    setForm({
      name: '',
      company_name: '',
      gst_number: '',
      email: '',
      phone: '',
      address: '',
      rating: 5.0,
      status: 'ACTIVE'
    });
    setIsModalOpen(true);
  };

  const openEditModal = (vendor) => {
    setIsEditing(true);
    setVendorId(vendor.id);
    setForm({
      name: vendor.name,
      company_name: vendor.company_name,
      gst_number: vendor.gst_number,
      email: vendor.email,
      phone: vendor.phone,
      address: vendor.address,
      rating: vendor.rating,
      status: vendor.status
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    // Basic validation
    if (!form.name || !form.company_name || !form.gst_number || !form.email || !form.phone || !form.address) {
      toast.error('All fields are required.');
      return;
    }

    try {
      if (isEditing) {
        const response = await api.put(`/vendors/${vendorId}`, form);
        if (response.data.success) {
          toast.success('Vendor updated successfully.');
          setIsModalOpen(false);
          fetchVendors();
        }
      } else {
        const response = await api.post('/vendors', form);
        if (response.data.success) {
          toast.success('Vendor registered successfully.');
          setIsModalOpen(false);
          fetchVendors();
        }
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Operation failed.');
    }
  };

  const openDeleteConfirm = (vendor) => {
    setSelectedVendor(vendor);
    setIsDeleteOpen(true);
  };

  const handleDelete = async () => {
    try {
      const response = await api.delete(`/vendors/${selectedVendor.id}`);
      if (response.data.success) {
        toast.success('Vendor deleted successfully.');
        setIsDeleteOpen(false);
        fetchVendors();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to delete vendor.');
    }
  };

  const handleExportExcel = async () => {
    try {
      const response = await api.get('/reports/vendors/excel', {
        params: { status: statusFilter || undefined },
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Vendor_Report_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Excel report downloaded.');
    } catch (e) {
      toast.error('Failed to download Excel report.');
    }
  };

  const headers = [
    { key: 'name', label: 'Vendor Name', sortable: true },
    { key: 'company_name', label: 'Company Name', sortable: true },
    { key: 'gst_number', label: 'GST Number' },
    { key: 'email', label: 'Email', sortable: true },
    { key: 'phone', label: 'Phone' },
    { key: 'rating', label: 'Rating', sortable: true, align: 'right', render: (row) => (
      <span style={{ fontWeight: '500' }}>★ {parseFloat(row.rating).toFixed(1)}</span>
    )},
    { key: 'status', label: 'Status', sortable: true, align: 'center', render: (row) => (
      <span className={`badge badge-${row.status.toLowerCase()}`}>{row.status}</span>
    )},
    {
      key: 'actions',
      label: 'Actions',
      align: 'center',
      render: (row) => (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '6px' }}>
          {hasRole(['Admin', 'Procurement Officer']) && (
            <>
              <Button variant="secondary" size="sm" onClick={() => openEditModal(row)} icon={Edit3}>
                Edit
              </Button>
              <Button variant="danger" size="sm" onClick={() => openDeleteConfirm(row)} icon={Trash2}>
                Delete
              </Button>
            </>
          )}
        </div>
      )
    }
  ];

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Vendors</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Manage supplier records, contact details, tax registry, and performance ratings.
          </span>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Button variant="secondary" onClick={handleExportExcel} icon={FileSpreadsheet}>
            Export Excel
          </Button>
          {hasRole(['Admin', 'Procurement Officer']) && (
            <Button variant="primary" onClick={openCreateModal} icon={Plus}>
              Register Vendor
            </Button>
          )}
        </div>
      </div>

      {/* Filter / Search Row */}
      <div className="card-enterprise" style={{ padding: '12px 16px', marginBottom: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flex: 1, minWidth: '240px', border: '1px solid var(--border)', borderRadius: '4px', overflow: 'hidden', backgroundColor: '#ffffff' }}>
            <input
              type="text"
              placeholder="Search by name, company, or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ flex: 1, padding: '6px 12px', border: 'none', outline: 'none', fontSize: '13px' }}
            />
            <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#f1f5f9', border: 'none', borderLeft: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text-secondary)' }}>
              <Search size={14} />
            </button>
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="form-select"
            style={{ width: '150px', padding: '6px 10px', height: '32px' }}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="SUSPENDED">Suspended</option>
          </select>
        </form>
      </div>

      {/* Main Table */}
      <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
        <Table
          headers={headers}
          data={vendors}
          isLoading={loading}
          onSort={handleSort}
          currentSort={sort}
        />
        
        {/* Pagination bar */}
        {!loading && totalPages > 1 && (
          <div className="flex-between" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--border)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Showing {vendors.length} of {totalVendors} vendors
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

      {/* Create / Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={isEditing ? 'Modify Vendor Record' : 'Register New Vendor Supplier'}
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsModalOpen(false), variant: 'secondary' },
          { label: isEditing ? 'Save Changes' : 'Register', onClick: handleSubmit, variant: 'primary' }
        ]}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="Vendor Name"
            name="name"
            value={form.name}
            onChange={handleInputChange}
            placeholder="e.g. Acme Corp IT"
            required
          />
          <Input
            label="Company Registration Name"
            name="company_name"
            value={form.company_name}
            onChange={handleInputChange}
            placeholder="e.g. Acme Corporation Pvt Ltd"
            required
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="GST Registration Number"
            name="gst_number"
            value={form.gst_number}
            onChange={handleInputChange}
            placeholder="15-digit AlphaNumeric code"
            required
          />
          <Input
            label="Supplier Email Address"
            name="email"
            type="email"
            value={form.email}
            onChange={handleInputChange}
            placeholder="sales@supplier.com"
            required
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="Business Contact Phone"
            name="phone"
            value={form.phone}
            onChange={handleInputChange}
            placeholder="+1-555-xxxx"
            required
          />
          <Input
            label="Rating (0.0 to 5.0)"
            name="rating"
            type="number"
            step="0.1"
            min="0"
            max="5"
            value={form.rating}
            onChange={handleInputChange}
            required
          />
        </div>
        <Input
          label="Corporate Status"
          name="status"
          type="select"
          value={form.status}
          onChange={handleInputChange}
          options={[
            { value: 'ACTIVE', label: 'Active' },
            { value: 'INACTIVE', label: 'Inactive' },
            { value: 'SUSPENDED', label: 'Suspended' }
          ]}
          required
        />
        <Input
          label="Billing / Shipping Address"
          name="address"
          type="textarea"
          value={form.address}
          onChange={handleInputChange}
          placeholder="Enter corporate physical address..."
          required
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        title="Confirm Vendor Deletion"
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsDeleteOpen(false), variant: 'secondary' },
          { label: 'Delete Supplier', onClick: handleDelete, variant: 'danger' }
        ]}
      >
        <p style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
          Are you sure you want to delete vendor <b>{selectedVendor?.name}</b>?
        </p>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px' }}>
          This operation is irreversible and will fail if active product references exist.
        </p>
      </Modal>
    </div>
  );
};

export default Vendors;
