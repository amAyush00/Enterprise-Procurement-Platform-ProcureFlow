import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Table from '../components/Table';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { Plus, Search, Edit3, Trash2 } from 'lucide-react';

const Products = () => {
  const { hasRole } = useAuth();
  const toast = useToast();

  // Data lists states
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters & Page state
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [vendorFilter, setVendorFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sort, setSort] = useState({ key: 'name', order: 'asc' });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);

  // Modal forms states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [productId, setProductId] = useState(null);
  const [form, setForm] = useState({
    name: '',
    sku: '',
    category_id: '',
    unit_price: '',
    reorder_level: 10,
    vendor_id: '',
    status: 'ACTIVE'
  });

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Fetch dropdown dependency options
  const fetchDropdowns = async () => {
    try {
      const catRes = await api.get('/products/categories');
      if (catRes.data.success) {
        setCategories(catRes.data.data);
      }
      
      // Fetch vendors for assigning to products
      const venRes = await api.get('/vendors', { params: { limit: 100 } });
      if (venRes.data.success) {
        setVendors(venRes.data.data.vendors);
      }
    } catch (e) {
      toast.error('Failed to load category or vendor details.');
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        limit: 10,
        sort_by: sort.key,
        sort_order: sort.order,
        search: search || undefined,
        category_id: categoryFilter || undefined,
        vendor_id: vendorFilter || undefined,
        status: statusFilter || undefined
      };

      const response = await api.get('/products', { params });
      if (response.data && response.data.success) {
        setProducts(response.data.data.products);
        setTotalPages(response.data.data.pages);
        setTotalProducts(response.data.data.total);
      }
    } catch (e) {
      toast.error('Failed to load products list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDropdowns();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [page, sort, categoryFilter, vendorFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
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
      sku: '',
      category_id: categories[0]?.id || '',
      unit_price: '',
      reorder_level: 10,
      vendor_id: vendors[0]?.id || '',
      status: 'ACTIVE'
    });
    setIsModalOpen(true);
  };

  const openEditModal = (product) => {
    setIsEditing(true);
    setProductId(product.id);
    setForm({
      name: product.name,
      sku: product.sku,
      category_id: product.category_id,
      unit_price: product.unit_price,
      reorder_level: product.reorder_level,
      vendor_id: product.vendor_id,
      status: product.status
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    if (!form.name || !form.sku || !form.category_id || !form.unit_price || !form.vendor_id) {
      toast.error('All fields are required.');
      return;
    }

    try {
      if (isEditing) {
        const response = await api.put(`/products/${productId}`, form);
        if (response.data.success) {
          toast.success('Product updated successfully.');
          setIsModalOpen(false);
          fetchProducts();
        }
      } else {
        const response = await api.post('/products', form);
        if (response.data.success) {
          toast.success('Product registered successfully.');
          setIsModalOpen(false);
          fetchProducts();
        }
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Operation failed.');
    }
  };

  const openDeleteConfirm = (product) => {
    setSelectedProduct(product);
    setIsDeleteOpen(true);
  };

  const handleDelete = async () => {
    try {
      const response = await api.delete(`/products/${selectedProduct.id}`);
      if (response.data.success) {
        toast.success('Product deleted successfully.');
        setIsDeleteOpen(false);
        fetchProducts();
      }
    } catch (e) {
      toast.error(e.response?.data?.message || 'Failed to delete product.');
    }
  };

  const headers = [
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'name', label: 'Product Name', sortable: true },
    { key: 'category_name', label: 'Category' },
    { key: 'vendor_name', label: 'Preferred Supplier' },
    { key: 'unit_price', label: 'Unit Price', sortable: true, align: 'right', render: (row) => (
      <span>₹{parseFloat(row.unit_price).toFixed(2)}</span>
    )},
    { key: 'available_quantity', label: 'Warehouse Stock', align: 'right', render: (row) => (
      <span style={{ fontWeight: '500', color: row.available_quantity <= row.reorder_level ? 'var(--danger)' : 'inherit' }}>
        {row.available_quantity} {row.available_quantity <= row.reorder_level && '⚠️'}
      </span>
    )},
    { key: 'reorder_level', label: 'Reorder Point', align: 'right' },
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
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: 'var(--text-primary)' }}>Products Catalog</h2>
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            Configure and maintain items, standard unit pricing, stock reorder levels, and preferred vendors.
          </span>
        </div>
        {hasRole(['Admin', 'Procurement Officer']) && (
          <Button variant="primary" onClick={openCreateModal} icon={Plus}>
            Add Catalog Product
          </Button>
        )}
      </div>

      {/* Filter / Search Panel */}
      <div className="card-enterprise" style={{ padding: '12px 16px', marginBottom: '16px' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flex: 1, minWidth: '200px', border: '1px solid var(--border)', borderRadius: '4px', overflow: 'hidden', backgroundColor: '#ffffff' }}>
            <input
              type="text"
              placeholder="Search by SKU or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ flex: 1, padding: '6px 12px', border: 'none', outline: 'none', fontSize: '13px' }}
            />
            <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#f1f5f9', border: 'none', borderLeft: '1px solid var(--border)', cursor: 'pointer', color: 'var(--text-secondary)' }}>
              <Search size={14} />
            </button>
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="form-select"
            style={{ width: '150px', padding: '6px 10px', height: '32px' }}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>

          <select
            value={vendorFilter}
            onChange={(e) => setVendorFilter(e.target.value)}
            className="form-select"
            style={{ width: '180px', padding: '6px 10px', height: '32px' }}
          >
            <option value="">All Preferred Suppliers</option>
            {vendors.map((v) => (
              <option key={v.id} value={v.id}>{v.name}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="form-select"
            style={{ width: '130px', padding: '6px 10px', height: '32px' }}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
            <option value="DISCONTINUED">Discontinued</option>
          </select>
        </form>
      </div>

      {/* Main Table */}
      <div className="card-enterprise" style={{ padding: '0', overflow: 'hidden' }}>
        <Table
          headers={headers}
          data={products}
          isLoading={loading}
          onSort={handleSort}
          currentSort={sort}
        />

        {!loading && totalPages > 1 && (
          <div className="flex-between" style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--border)' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              Showing {products.length} of {totalProducts} products
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
        title={isEditing ? 'Modify Catalog Product' : 'Add New Catalog Product'}
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsModalOpen(false), variant: 'secondary' },
          { label: isEditing ? 'Save Changes' : 'Create Product', onClick: handleSubmit, variant: 'primary' }
        ]}
      >
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="Product Name"
            name="name"
            value={form.name}
            onChange={handleInputChange}
            placeholder="e.g. Dell Latitude 5440"
            required
          />
          <Input
            label="SKU Identifier"
            name="sku"
            value={form.sku}
            onChange={handleInputChange}
            placeholder="e.g. HW-DELL-LAT5440"
            required
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="Category"
            name="category_id"
            type="select"
            value={form.category_id}
            onChange={handleInputChange}
            options={categories.map(c => ({ value: c.id, label: c.name }))}
            required
          />
          <Input
            label="Preferred Supplier"
            name="vendor_id"
            type="select"
            value={form.vendor_id}
            onChange={handleInputChange}
            options={vendors.map(v => ({ value: v.id, label: v.name }))}
            required
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <Input
            label="Standard Price (INR)"
            name="unit_price"
            type="number"
            step="0.01"
            min="0"
            value={form.unit_price}
            onChange={handleInputChange}
            placeholder="e.g. 999.00"
            required
          />
          <Input
            label="Reorder Limit Level"
            name="reorder_level"
            type="number"
            min="0"
            value={form.reorder_level}
            onChange={handleInputChange}
            required
          />
        </div>
        <Input
          label="Catalog Status"
          name="status"
          type="select"
          value={form.status}
          onChange={handleInputChange}
          options={[
            { value: 'ACTIVE', label: 'Active' },
            { value: 'INACTIVE', label: 'Inactive' },
            { value: 'DISCONTINUED', label: 'Discontinued' }
          ]}
          required
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        title="Confirm Product Deletion"
        footerButtons={[
          { label: 'Cancel', onClick: () => setIsDeleteOpen(false), variant: 'secondary' },
          { label: 'Delete Product', onClick: handleDelete, variant: 'danger' }
        ]}
      >
        <p style={{ fontSize: '13px', color: 'var(--text-primary)' }}>
          Are you sure you want to delete product <b>{selectedProduct?.name}</b>?
        </p>
        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px' }}>
          This operation will fail if the product has associated transaction ledger entries, purchase requests, or purchase orders.
        </p>
      </Modal>
    </div>
  );
};

export default Products;
