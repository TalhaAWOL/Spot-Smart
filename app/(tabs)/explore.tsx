import axios from 'axios';
import * as Location from 'expo-location';
import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

interface ParkingLot {
  lot_id: string;
  name: string;
  address: string;
  coordinates: { latitude: number; longitude: number };
  stats: {
    available_spaces: number;
    total_spaces: number;
    cars_detected: number;
  };
  distance?: number;
}

export default function ExploreScreen() {
  const [parkingLots, setParkingLots] = useState<ParkingLot[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchParkingLots();
  }, []);

  const fetchParkingLots = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      // Get user location
      const { coords } = await Location.getCurrentPositionAsync({});

      // Fetch parking lots from backend
      const res = await axios.get('http://10.0.2.2:8000/api/parking/lots');

      if (res.data.success) {
        // Calculate distance and sort by nearest
        const lotsWithDistance = res.data.parking_lots
          .map((lot: ParkingLot) => ({
            ...lot,
            address: lot.address || 'Address not available',
            distance: calculateDistance(
              coords.latitude,
              coords.longitude,
              lot.coordinates.latitude,
              lot.coordinates.longitude
            ),
          }))
          .sort((a: ParkingLot, b: ParkingLot) => (a.distance || 0) - (b.distance || 0));

        setParkingLots(lotsWithDistance);
      }
    } catch (error) {
      console.error('Error fetching parking lots:', error);
      // Fallback to mock data for testing
      setMockData();
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const setMockData = () => {
    // Mock data for testing UI
    setParkingLots([
      {
        lot_id: '1',
        name: 'Sheridan Davis Campus',
        address: '1001 Fanshawe College Blvd, London, ON',
        coordinates: { latitude: 43.655606, longitude: -79.738649 },
        stats: { available_spaces: 45, total_spaces: 100, cars_detected: 55 },
        distance: 0.5,
      },
      {
        lot_id: '2',
        name: 'Main Street Parking',
        address: '123 Main St, Brampton, ON',
        coordinates: { latitude: 43.6532, longitude: -79.7832 },
        stats: { available_spaces: 12, total_spaces: 50, cars_detected: 38 },
        distance: 2.3,
      },
    ]);
  };

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371; // Earth's radius in km
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLon = ((lon2 - lon1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const handleLotPress = (lot: ParkingLot) => {
    // Navigate to map tab and pass the selected lot
    router.push({
      pathname: '/(tabs)',
      params: {
        selectedLotId: lot.lot_id,
        latitude: lot.coordinates.latitude,
        longitude: lot.coordinates.longitude,
      },
    });
  };

  const renderLotItem = ({ item }: { item: ParkingLot }) => {
    const occupancyRate = Math.round(
      ((item.stats.total_spaces - item.stats.available_spaces) / item.stats.total_spaces) * 100
    );

    return (
      <TouchableOpacity style={styles.lotCard} onPress={() => handleLotPress(item)}>
        <View style={styles.lotHeader}>
          <Text style={styles.lotName} numberOfLines={1}>
            {item.name}
          </Text>
          {item.distance !== undefined && (
            <Text style={styles.distance}>{item.distance.toFixed(1)} km</Text>
          )}
        </View>

        <Text style={styles.address} numberOfLines={2}>
          {item.address}
        </Text>

        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Available</Text>
            <Text
              style={[
                styles.statValue,
                { color: item.stats.available_spaces > 0 ? '#28a745' : '#dc3545' },
              ]}>
              {item.stats.available_spaces}
            </Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Total</Text>
            <Text style={styles.statValue}>{item.stats.total_spaces}</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statLabel}>Occupancy</Text>
            <Text style={styles.statValue}>{occupancyRate}%</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#0066cc" />
        <Text style={styles.loadingText}>Loading parking lots...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Nearby Parking</Text>
        <Text style={styles.headerSubtitle}>Sorted by distance</Text>
      </View>

      <FlatList
        data={parkingLots}
        renderItem={renderLotItem}
        keyExtractor={(item) => item.lot_id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => fetchParkingLots(true)}
            tintColor="#0066cc"
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No parking lots found nearby</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: 'white',
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
  listContent: {
    padding: 15,
  },
  lotCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  lotHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  lotName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
    marginRight: 10,
  },
  distance: {
    fontSize: 14,
    color: '#0066cc',
    fontWeight: '600',
  },
  address: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 12,
  },
  stat: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#999',
  },
});