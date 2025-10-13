import React, { useState, useEffect } from 'react';
import { 
  Box, CircularProgress, Typography, Chip, Dialog, DialogTitle, 
  DialogContent, List, ListItem, ListItemText, Divider, Grid,
  Menu, MenuItem, Button, Snackbar, Alert, TextField
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { Visibility as ViewIcon, Search as SearchIcon } from '@mui/icons-material';

// --- SIMULACIÓN DE DATOS Y API ---
const mockOrdersData = [
  { 
    id: '#1256', 
    customer: { name: 'Juan Pérez', email: 'juan.perez@email.com' },
    date: '2025-10-08T10:30:00Z', 
    total: 84.98, 
    status: 'Completado',
    shippingAddress: 'Av. Siempre Viva 123, Springfield',
    products: [
      { id: 1, name: 'Proteína Whey Gold', quantity: 1, price: 59.99 },
      { id: 2, name: 'Creatina Monohidratada', quantity: 1, price: 24.99 },
    ]
  },
  { 
    id: '#1255', 
    customer: { name: 'Ana Gómez', email: 'ana.gomez@email.com' },
    date: '2025-10-08T09:15:00Z', 
    total: 112.50, 
    status: 'Enviado',
    shippingAddress: 'Calle Falsa 456, Shelbyville',
    products: [
      { id: 3, name: 'BCAAs en Polvo', quantity: 2, price: 34.50 },
      { id: 1, name: 'Proteína Whey Gold', quantity: 1, price: 59.99 },
    ]
  },
  { 
    id: '#1254', 
    customer: { name: 'Carlos Ruiz', email: 'carlos.ruiz@email.com' },
    date: '2025-10-07T18:00:00Z', 
    total: 45.00, 
    status: 'Pendiente',
    shippingAddress: 'Blvd. de los Sueños Rotos 789, Capital City',
    products: [
      { id: 2, name: 'Creatina Monohidratada', quantity: 1, price: 24.99 },
      { id: 4, name: 'Shaker Pro', quantity: 1, price: 20.01 },
    ]
  },
];
const statusOptions = ['Pendiente', 'Procesando', 'Enviado', 'Completado', 'Cancelado'];
const statusChipColor = {
  'Completado': 'success', 'Enviado': 'info', 'Procesando': 'primary', 
  'Pendiente': 'warning', 'Cancelado': 'error',
};

const fetchOrdersApi = async () => { await new Promise(r => setTimeout(r, 1000)); return mockOrdersData; };
const updateOrderStatusApi = async (orderId, newStatus) => { await new Promise(r => setTimeout(r, 500)); const order = mockOrdersData.find(o => o.id === orderId); if (order) order.status = newStatus; return order; };

function OrdersPage() {
  // --- ESTADOS DEL COMPONENTE ---
  const [orders, setOrders] = useState([]);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [statusMenu, setStatusMenu] = useState({ anchorEl: null, orderId: null });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [searchText, setSearchText] = useState('');

  // --- EFECTOS ---
  useEffect(() => {
    loadOrders();
  }, []);

  useEffect(() => {
    // Este efecto se ejecuta cada vez que el texto de búsqueda cambia
    const filtered = orders.filter(order => 
      order.id.toLowerCase().includes(searchText.toLowerCase()) ||
      order.customer.name.toLowerCase().includes(searchText.toLowerCase())
    );
    setFilteredOrders(filtered);
  }, [searchText, orders]);

  // --- MANEJADORES DE LÓGICA ---
  const loadOrders = async () => {
    setLoading(true);
    try {
      const fetchedOrders = await fetchOrdersApi();
      setOrders(fetchedOrders);
      setFilteredOrders(fetchedOrders);
    } catch (error) {
      setSnackbar({ open: true, message: 'Error al cargar los pedidos', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = (order) => setSelectedOrder(order);
  const handleCloseDetails = () => setSelectedOrder(null);
  const handleStatusMenuOpen = (event, orderId) => setStatusMenu({ anchorEl: event.currentTarget, orderId });
  const handleStatusMenuClose = () => setStatusMenu({ anchorEl: null, orderId: null });

  const handleStatusUpdate = async (newStatus) => {
    const { orderId } = statusMenu;
    handleStatusMenuClose();
    try {
      await updateOrderStatusApi(orderId, newStatus);
      setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
      setSnackbar({ open: true, message: `Estado del pedido ${orderId} actualizado`, severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Error al actualizar el estado', severity: 'error' });
    }
  };

  // --- DEFINICIÓN DE COLUMNAS (CORREGIDA Y ROBUSTA) ---
  const columns = [
    { field: 'id', headerName: 'ID Pedido', width: 120 },
    { 
      field: 'customerName', 
      headerName: 'Cliente', 
      width: 200,
      valueGetter: (value, row) => row.customer?.name || ''
    },
    { 
      field: 'date', 
      headerName: 'Fecha', 
      width: 180, 
      type: 'dateTime',
      valueGetter: (value, row) => new Date(row.date) 
    },
    { 
      field: 'total', 
      headerName: 'Total', 
      width: 120, 
      type: 'number',
      renderCell: (params) => <Typography>{`$${params.value.toFixed(2)}`}</Typography>
    },
    {
      field: 'status',
      headerName: 'Estado',
      width: 150,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={statusChipColor[params.value] || 'default'} 
          size="small"
          onClick={(e) => handleStatusMenuOpen(e, params.row.id)}
          sx={{ cursor: 'pointer', textTransform: 'capitalize', fontWeight: 'bold' }}
        />
      ),
    },
    {
      field: 'actions',
      headerName: 'Acciones',
      sortable: false,
      filterable: false,
      width: 120,
      renderCell: (params) => (
        <Button startIcon={<ViewIcon />} onClick={() => handleViewDetails(params.row)} size="small">
          Detalles
        </Button>
      ),
    },
  ];

  // --- RENDERIZADO DEL COMPONENTE ---
  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">Gestión de Pedidos</Typography>
        <TextField
          variant="outlined"
          size="small"
          placeholder="Buscar por ID o cliente..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.disabled' }} />,
          }}
        />
      </Box>

      <Box sx={{ height: '70vh', width: '100%' }}>
        <DataGrid
          rows={filteredOrders}
          columns={columns}
          loading={loading}
          pageSizeOptions={[10, 25, 50]}
          initialState={{ pagination: { paginationModel: { pageSize: 10 } }}}
          disableRowSelectionOnClick
        />
      </Box>

      {/* Menú para cambiar el estado */}
      <Menu anchorEl={statusMenu.anchorEl} open={Boolean(statusMenu.anchorEl)} onClose={handleStatusMenuClose}>
        {statusOptions.map((status) => (
          <MenuItem key={status} onClick={() => handleStatusUpdate(status)}>{status}</MenuItem>
        ))}
      </Menu>

      {/* Modal para ver detalles del pedido */}
      <Dialog open={Boolean(selectedOrder)} onClose={handleCloseDetails} fullWidth maxWidth="sm">
        {selectedOrder && (
          <>
            <DialogTitle>Detalles del Pedido: {selectedOrder.id}</DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="h6">Información del Cliente</Typography>
                  <Typography><b>Nombre:</b> {selectedOrder.customer.name}</Typography>
                  <Typography><b>Email:</b> {selectedOrder.customer.email}</Typography>
                  <Typography><b>Dirección de Envío:</b> {selectedOrder.shippingAddress}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="h6">Productos en el Pedido</Typography>
                  <List dense>
                    {selectedOrder.products.map(p => (
                      <ListItem key={p.id}>
                        <ListItemText 
                          primary={`${p.name} (x${p.quantity})`}
                          secondary={`Precio unitario: $${p.price.toFixed(2)}`}
                        />
                        <Typography variant="body1"><b>${(p.quantity * p.price).toFixed(2)}</b></Typography>
                      </ListItem>
                    ))}
                  </List>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ textAlign: 'right', pr: 2 }}>
                    <Typography variant="h6">Total: ${selectedOrder.total.toFixed(2)}</Typography>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDetails}>Cerrar</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* Notificación de Feedback */}
      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({...snackbar, open: false})} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert severity={snackbar.severity} sx={{ width: '100%' }} onClose={() => setSnackbar({...snackbar, open: false})}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default OrdersPage;