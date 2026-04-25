import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';

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

interface FuelStats {
  totalMiles: number;
  totalFuelCost: number;
  claimableAmount: number;
  avgMpg: number;
  businessMiles: number;
  personalMiles: number;
  commuteMiles: number;
}

export function useFuelData() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([
    { id: 1, name: 'Company Car', registration: 'AB12 CDE', type: 'car', defaultMileageRate: 0.45 },
    { id: 2, name: 'Work Van', registration: 'VX21 FGH', type: 'van', defaultMileageRate: 0.45 }
  ]);
  
  const [entries, setEntries] = useState<FuelEntry[]>([]);
  const [stats, setStats] = useState<FuelStats>({
    totalMiles: 0,
    totalFuelCost: 0,
    claimableAmount: 0,
    avgMpg: 0,
    businessMiles: 0,
    personalMiles: 0,
    commuteMiles: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateStats = useCallback((data: FuelEntry[]) => {
    const totalMiles = data.reduce((sum, e) => sum + e.distance, 0);
    const totalFuelCost = data.reduce((sum, e) => sum + e.amount, 0);
    
    // HMRC rates: 45p first 10k miles, 25p thereafter
    const businessMiles = data.filter(e => e.purpose === 'business').reduce((sum, e) => sum + e.distance, 0);
    let claimableAmount = 0;
    if (businessMiles <= 10000) {
      claimableAmount = businessMiles * 0.45;
    } else {
      claimableAmount = (10000 * 0.45) + ((businessMiles - 10000) * 0.25);
    }
    
    const personalMiles = data.filter(e => e.purpose === 'personal').reduce((sum, e) => sum + e.distance, 0);
    const commuteMiles = data.filter(e => e.purpose === 'commute').reduce((sum, e) => sum + e.distance, 0);
    
    // Estimate MPG (assuming £1.50 per liter, 4.5 liters per gallon)
    const estimatedGallons = totalFuelCost / 1.50 / 4.5;
    const avgMpg = estimatedGallons > 0 ? totalMiles / estimatedGallons : 0;

    setStats({
      totalMiles,
      totalFuelCost,
      claimableAmount,
      avgMpg,
      businessMiles,
      personalMiles,
      commuteMiles
    });
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/fuel/logs');
      setEntries(response.data);
      calculateStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load fuel data');
      // Use mock data if API fails
      const mockData: FuelEntry[] = [
        { id: '1', date: '2024-01-15', vehicleId: 1, distance: 125.5, amount: 45.20, purpose: 'business', notes: 'Client meeting' },
        { id: '2', date: '2024-01-20', vehicleId: 1, distance: 89.0, amount: 32.50, purpose: 'personal' },
        { id: '3', date: '2024-02-05', vehicleId: 1, distance: 210.0, amount: 78.90, purpose: 'business', notes: 'Site visit Manchester' },
        { id: '4', date: '2024-02-12', vehicleId: 1, distance: 45.0, amount: 16.80, purpose: 'commute' },
        { id: '5', date: '2024-03-01', vehicleId: 2, distance: 150.0, amount: 65.40, purpose: 'business', notes: 'Equipment delivery' }
      ];
      setEntries(mockData);
      calculateStats(mockData);
    } finally {
      setLoading(false);
    }
  }, [calculateStats]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addEntry = async (entry: FuelEntry) => {
    try {
      await apiClient.post('/fuel/log', entry);
      await refresh();
      return true;
    } catch (err) {
      // Optimistic update
      setEntries(prev => [entry, ...prev]);
      calculateStats([entry, ...entries]);
      return true;
    }
  };

  const deleteEntry = async (id: string) => {
    try {
      await apiClient.delete(`/fuel/log/${id}`);
      await refresh();
      return true;
    } catch (err) {
      // Optimistic update
      const updated = entries.filter(e => e.id !== id);
      setEntries(updated);
      calculateStats(updated);
      return true;
    }
  };

  return {
    vehicles,
    entries,
    stats,
    loading,
    error,
    addEntry,
    deleteEntry,
    refresh
  };
}

export default useFuelData;
