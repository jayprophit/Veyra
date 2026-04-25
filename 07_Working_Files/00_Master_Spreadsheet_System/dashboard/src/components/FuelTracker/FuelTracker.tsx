import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  LocalGasStation as FuelIcon,
  TrendingUp as TrendingUpIcon,
  Receipt as ReceiptIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useFuelData } from '../../hooks/useFuelData';
import './FuelTracker.css';

interface Vehicle {
  id: number;
  name: string;
  registration: string;
  type: 'car' | 'van' | 'motorcycle';
  defaultMileageRate: number;
}

interface FuelEntry {
  id: string;
  date: string;
  vehicleId: number;
  distance: number;
  amount: number;
  purpose: 'business' | 'personal' | 'commute';
  notes?: string;
}

const PURPOSE_COLORS = {
  business: '#4caf50',
  personal: '#ff9800',
  commute: '#2196f3'
};

const VEHICLE_TYPE_ICONS = {
  car: '🚗',
  van: '🚐',
  motorcycle: '🏍️'
};

export const FuelTracker: React.FC = () => {
  const { vehicles, entries, stats, loading, addEntry, deleteEntry, refresh } = useFuelData();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState<number>(1);
  const [newEntry, setNewEntry] = useState<Partial<FuelEntry>>({
    date: new Date().toISOString().split('T')[0],
    purpose: 'business',
    distance: 0,
    amount: 0,
    notes: ''
  });
  const [notification, setNotification] = useState<{message: string, severity: 'success' | 'error'} | null>(null);
  const [hmrcDialogOpen, setHmrcDialogOpen] = useState(false);

  const handleAddEntry = async () => {
    if (!newEntry.distance || !newEntry.amount) {
      setNotification({ message: 'Please fill in all required fields', severity: 'error' });
      return;
    }

    try {
      await addEntry({
        ...newEntry,
        vehicleId: selectedVehicle,
        id: Date.now().toString()
      } as FuelEntry);
      
      setNotification({ message: 'Fuel entry added successfully', severity: 'success' });
      setOpenDialog(false);
      setNewEntry({
        date: new Date().toISOString().split('T')[0],
        purpose: 'business',
        distance: 0,
        amount: 0,
        notes: ''
      });
      refresh();
    } catch (error) {
      setNotification({ message: 'Failed to add entry', severity: 'error' });
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this entry?')) {
      await deleteEntry(id);
      refresh();
      setNotification({ message: 'Entry deleted', severity: 'success' });
    }
  };

  const calculateClaimableAmount = (entry: FuelEntry) => {
    const vehicle = vehicles.find(v => v.id === entry.vehicleId);
    if (!vehicle || entry.purpose !== 'business') return 0;
    
    // HMRC rates: 45p for first 10,000 miles, 25p thereafter
    const miles = entry.distance;
    const rate = miles <= 10000 ? 0.45 : 0.25;
    return miles * rate;
  };

  const chartData = entries.slice(-12).map(entry => ({
    date: new Date(entry.date).toLocaleDateString('en-GB', { month: 'short', day: 'numeric' }),
    distance: entry.distance,
    claimable: calculateClaimableAmount(entry)
  }));

  const purposeData = [
    { name: 'Business', value: entries.filter(e => e.purpose === 'business').length, color: PURPOSE_COLORS.business },
    { name: 'Personal', value: entries.filter(e => e.purpose === 'personal').length, color: PURPOSE_COLORS.personal },
    { name: 'Commute', value: entries.filter(e => e.purpose === 'commute').length, color: PURPOSE_COLORS.commute }
  ];

  return (
    <Box className="fuel-tracker-container">
      <Typography variant="h4" gutterBottom className="fuel-tracker-title">
        <FuelIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Fuel & Mileage Tracker
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} className="stats-grid">
        <Grid item xs={12} sm={6} md={3}>
          <Card className="stat-card">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Miles This Year
              </Typography>
              <Typography variant="h4" className="stat-value">
                {stats.totalMiles.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                miles driven
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="stat-card claimable">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                HMRC Claimable
              </Typography>
              <Typography variant="h4" className="stat-value claimable-amount">
                £{stats.claimableAmount.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                tax deductible
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="stat-card">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Fuel Spent
              </Typography>
              <Typography variant="h4" className="stat-value">
                £{stats.totalFuelCost.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                this year
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card className="stat-card">
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                MPG Average
              </Typography>
              <Typography variant="h4" className="stat-value">
                {stats.avgMpg.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                miles per gallon
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} className="charts-grid">
        <Grid item xs={12} md={8}>
          <Paper className="chart-paper">
            <Typography variant="h6" gutterBottom>
              <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Mileage Trend
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Line yAxisId="left" type="monotone" dataKey="distance" stroke="#2196f3" name="Distance (miles)" />
                <Line yAxisId="right" type="monotone" dataKey="claimable" stroke="#4caf50" name="Claimable (£)" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper className="chart-paper">
            <Typography variant="h6" gutterBottom>
              Trip Purpose Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={purposeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {purposeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box className="chart-legend">
              {purposeData.map(item => (
                <Box key={item.name} className="legend-item">
                  <Box className="legend-color" sx={{ backgroundColor: item.color }} />
                  <Typography variant="body2">{item.name}: {item.value}</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box className="action-buttons">
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
          className="add-button"
        >
          Log Fuel Purchase
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<ReceiptIcon />}
          onClick={() => setHmrcDialogOpen(true)}
          className="hmrc-button"
        >
          Generate HMRC Report
        </Button>
      </Box>

      {/* Entries Table */}
      <TableContainer component={Paper} className="entries-table">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Vehicle</TableCell>
              <TableCell>Distance (miles)</TableCell>
              <TableCell>Amount (£)</TableCell>
              <TableCell>Purpose</TableCell>
              <TableCell>Claimable (£)</TableCell>
              <TableCell>Notes</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((entry) => {
              const vehicle = vehicles.find(v => v.id === entry.vehicleId);
              return (
                <TableRow key={entry.id}>
                  <TableCell>{new Date(entry.date).toLocaleDateString('en-GB')}</TableCell>
                  <TableCell>
                    {VEHICLE_TYPE_ICONS[vehicle?.type || 'car']} {vehicle?.name}
                  </TableCell>
                  <TableCell>{entry.distance.toFixed(1)}</TableCell>
                  <TableCell>£{entry.amount.toFixed(2)}</TableCell>
                  <TableCell>
                    <Box
                      className="purpose-badge"
                      sx={{ backgroundColor: PURPOSE_COLORS[entry.purpose] }}
                    >
                      {entry.purpose}
                    </Box>
                  </TableCell>
                  <TableCell className={calculateClaimableAmount(entry) > 0 ? 'claimable-cell' : ''}>
                    £{calculateClaimableAmount(entry).toFixed(2)}
                  </TableCell>
                  <TableCell>{entry.notes}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleDelete(entry.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Entry Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Log Fuel Purchase</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} className="dialog-content">
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Vehicle</InputLabel>
                <Select
                  value={selectedVehicle}
                  onChange={(e) => setSelectedVehicle(Number(e.target.value))}
                >
                  {vehicles.map(v => (
                    <MenuItem key={v.id} value={v.id}>
                      {VEHICLE_TYPE_ICONS[v.type]} {v.name} ({v.registration})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Date"
                value={newEntry.date}
                onChange={(e) => setNewEntry({ ...newEntry, date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Purpose</InputLabel>
                <Select
                  value={newEntry.purpose}
                  onChange={(e) => setNewEntry({ ...newEntry, purpose: e.target.value as any })}
                >
                  <MenuItem value="business">💼 Business</MenuItem>
                  <MenuItem value="personal">🏠 Personal</MenuItem>
                  <MenuItem value="commute">🚗 Commute</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Distance (miles)"
                value={newEntry.distance}
                onChange={(e) => setNewEntry({ ...newEntry, distance: Number(e.target.value) })}
                helperText={newEntry.purpose === 'business' ? 'HMRC claimable at 45p/mile' : ''}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Fuel Cost (£)"
                value={newEntry.amount}
                onChange={(e) => setNewEntry({ ...newEntry, amount: Number(e.target.value) })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Notes (optional)"
                value={newEntry.notes}
                onChange={(e) => setNewEntry({ ...newEntry, notes: e.target.value })}
                placeholder="e.g., Client meeting in London"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddEntry} variant="contained" color="primary">
            Save Entry
          </Button>
        </DialogActions>
      </Dialog>

      {/* HMRC Report Dialog */}
      <Dialog open={hmrcDialogOpen} onClose={() => setHmrcDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>HMRC Mileage Claim Report</DialogTitle>
        <DialogContent>
          <Box className="hmrc-report">
            <Typography variant="h6" gutterBottom>
              Tax Year 2024/25 Summary
            </Typography>
            
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Period</TableCell>
                    <TableCell align="right">Business Miles</TableCell>
                    <TableCell align="right">Rate</TableCell>
                    <TableCell align="right">Amount</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>First 10,000 miles</TableCell>
                    <TableCell align="right">{Math.min(stats.totalMiles, 10000).toLocaleString()}</TableCell>
                    <TableCell align="right">45p</TableCell>
                    <TableCell align="right">£{Math.min(stats.totalMiles, 10000 * 0.45).toFixed(2)}</TableCell>
                  </TableRow>
                  {stats.totalMiles > 10000 && (
                    <TableRow>
                      <TableCell>Above 10,000 miles</TableCell>
                      <TableCell align="right">{(stats.totalMiles - 10000).toLocaleString()}</TableCell>
                      <TableCell align="right">25p</TableCell>
                      <TableCell align="right">£{((stats.totalMiles - 10000) * 0.25).toFixed(2)}</TableCell>
                    </TableRow>
                  )}
                  <TableRow className="total-row">
                    <TableCell colSpan={3}><strong>Total Claimable</strong></TableCell>
                    <TableCell align="right"><strong>£{stats.claimableAmount.toFixed(2)}</strong></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box className="hmrc-note" sx={{ mt: 2 }}>
              <Alert severity="info">
                <Typography variant="body2">
                  This report is ready for your Self Assessment tax return. 
                  Keep receipts for fuel purchases as supporting evidence.
                </Typography>
              </Alert>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHmrcDialogOpen(false)}>Close</Button>
          <Button variant="contained" color="primary">
            Download PDF
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification */}
      <Snackbar
        open={!!notification}
        autoHideDuration={6000}
        onClose={() => setNotification(null)}
      >
        <Alert severity={notification?.severity || 'info'} onClose={() => setNotification(null)}>
          {notification?.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FuelTracker;
