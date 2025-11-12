import axios from "axios";
import Constants from 'expo-constants';
import * as Location from "expo-location";
import { useLocalSearchParams } from 'expo-router';
import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import MapView, { Marker, Polyline, Region } from "react-native-maps";
const extra = Constants.expoConfig?.extra || {};
const GOOGLE_MAPS_KEY = extra.GOOGLE_MAPS_KEY;

interface ParkingData {
  car_count: number;
  available_spaces: number;
  total_spaces: number;
}

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
  video_filename?: string;
}

export default function HomeScreen() {
  const mapRef = useRef<MapView>(null);
  const [region, setRegion] = useState<Region | null>(null);
  const [routeCoords, setRouteCoords] = useState<{ latitude: number; longitude: number }[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [parkingData, setParkingData] = useState<ParkingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [parkingLots, setParkingLots] = useState<ParkingLot[]>([]);
  const [selectedLot, setSelectedLot] = useState<ParkingLot | null>(null);
  const params = useLocalSearchParams();

  // Fetch parking lots from backend
  const fetchParkingLots = async () => {
    try {
      const res = await axios.get("http://10.0.2.2:8000/api/parking/lots");
      if (res.data.success) {
        setParkingLots(res.data.parking_lots);
      }
    } catch (error) {
      console.error("Error fetching parking lots:", error);
    }
  };

  useEffect(() => {
    fetchParkingLots();
  }, []);

  useEffect(() => {
    // Handle navigation from list view
    if (params.selectedLotId) {
      const lat = parseFloat(params.latitude as string);
      const lon = parseFloat(params.longitude as string);
      
      // Find the selected lot
      const lot = parkingLots.find(l => l.lot_id === params.selectedLotId);
      if (lot) {
        setSelectedLot(lot);
      }
      
      mapRef.current?.animateToRegion({
        latitude: lat,
        longitude: lon,
        latitudeDelta: 0.005,
        longitudeDelta: 0.005,
      }, 1000);
    }
  }, [params, parkingLots]);

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permission denied", "Location access is required to show your position.");
        // Fallback to first parking lot or default location
        if (parkingLots.length > 0) {
          setRegion({
            latitude: parkingLots[0].coordinates.latitude,
            longitude: parkingLots[0].coordinates.longitude,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
          });
        } else {
          setRegion({
            latitude: 43.655606,
            longitude: -79.738649,
            latitudeDelta: 0.05,
            longitudeDelta: 0.05,
          });
        }
        return;
      }

      try {
        // Retry logic for location
        let userLoc = null;
        for (let i = 0; i < 3; i++) {
          try {
            userLoc = await Location.getCurrentPositionAsync({
              accuracy: Location.Accuracy.Balanced,
            });
            break;
          } catch {
            await new Promise((r) => setTimeout(r, 1000));
          }
        }

        if (!userLoc) {
          // Fallback to first parking lot location
          if (parkingLots.length > 0) {
            setRegion({
              latitude: parkingLots[0].coordinates.latitude,
              longitude: parkingLots[0].coordinates.longitude,
              latitudeDelta: 0.05,
              longitudeDelta: 0.05,
            });
          } else {
            setRegion({
              latitude: 43.655606,
              longitude: -79.738649,
              latitudeDelta: 0.05,
              longitudeDelta: 0.05,
            });
          }
          return;
        }

        // Start from user location
        setRegion({
          latitude: userLoc.coords.latitude,
          longitude: userLoc.coords.longitude,
          latitudeDelta: 0.05,
          longitudeDelta: 0.05,
        });

        // If we have parking lots, zoom to show all of them
        if (parkingLots.length > 0) {
          setTimeout(() => {
            fitMapToMarkers();
          }, 1500);
        }
      } catch (error) {
        // Fallback to default location
        setRegion({
          latitude: 43.655606,
          longitude: -79.738649,
          latitudeDelta: 0.05,
          longitudeDelta: 0.05,
        });
      }
    })();
  }, [parkingLots]);

  const fitMapToMarkers = () => {
    if (parkingLots.length === 0) return;

    const coordinates = parkingLots.map(lot => ({
      latitude: lot.coordinates.latitude,
      longitude: lot.coordinates.longitude,
    }));

    mapRef.current?.fitToCoordinates(coordinates, {
      edgePadding: { top: 50, right: 50, bottom: 50, left: 50 },
      animated: true,
    });
  };

  const callAIDetection = async (lot: ParkingLot) => {
    setLoading(true);
    try {
      const res = await axios.post("http://10.0.2.2:8000/api/parking/analyze-video", {
        lot_id: lot.lot_id,
        video_filename: lot.video_filename || "parking_video.mp4",
        frame_number: 100,
      });

      if (res.data.success) {
        setParkingData({
          car_count: res.data.car_count,
          available_spaces: res.data.parking_analysis.available_spaces,
          total_spaces: res.data.parking_analysis.total_spaces,
        });
        
        // Refresh parking lots to get updated stats
        fetchParkingLots();
      } else {
        Alert.alert("Detection failed", "AI did not return valid results.");
      }
    } catch (error) {
      Alert.alert("Error", "Could not connect to AI backend.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const navigateTo = async () => {
    if (!selectedLot) return;

    try {
      const { coords } = await Location.getCurrentPositionAsync({});
      const origin = `${coords.latitude},${coords.longitude}`;
      const dest = `${selectedLot.coordinates.latitude},${selectedLot.coordinates.longitude}`;

      const url = `https://maps.googleapis.com/maps/api/directions/json?origin=${origin}&destination=${dest}&key=${GOOGLE_MAPS_KEY}`;
      const res = await axios.get(url);

      if (res.data.routes && res.data.routes.length > 0) {
        const points = decodePolyline(res.data.routes[0].overview_polyline.points);
        setRouteCoords(points);
        setModalVisible(false);
        Alert.alert("Navigation", "Route has been drawn on the map!");
      } else {
        Alert.alert("Navigation error", "Could not find a route.");
      }
    } catch (error) {
      Alert.alert("Navigation error", "Could not get directions.");
      console.error(error);
    }
  };

  const decodePolyline = (encoded: string) => {
    let points: { latitude: number; longitude: number }[] = [];
    let index = 0,
      lat = 0,
      lng = 0;

    while (index < encoded.length) {
      let b,
        shift = 0,
        result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const dlat = result & 1 ? ~(result >> 1) : result >> 1;
      lat += dlat;

      shift = 0;
      result = 0;
      do {
        b = encoded.charCodeAt(index++) - 63;
        result |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      const dlng = result & 1 ? ~(result >> 1) : result >> 1;
      lng += dlng;

      points.push({ latitude: lat / 1e5, longitude: lng / 1e5 });
    }

    return points;
  };

  const handleMarkerPress = (lot: ParkingLot) => {
    setSelectedLot(lot);
    setParkingData(null);
    setModalVisible(true);
    callAIDetection(lot);
  };

  const getMarkerColor = (lot: ParkingLot) => {
    const availabilityRate = lot.stats.available_spaces / lot.stats.total_spaces;
    if (availabilityRate > 0.5) return "green";
    if (availabilityRate > 0.2) return "orange";
    return "red";
  };

  if (!region) {
    return <ActivityIndicator size="large" color="#0066cc" style={{ flex: 1 }} />;
  }

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        initialRegion={region}
        showsUserLocation
        showsMyLocationButton
        zoomEnabled={true}
        scrollEnabled={true}
        pitchEnabled={true}
        rotateEnabled={true}
      >
        {parkingLots.map((lot) => (
          <Marker
            key={lot.lot_id}
            coordinate={{
              latitude: lot.coordinates.latitude,
              longitude: lot.coordinates.longitude,
            }}
            title={lot.name}
            description={`Available: ${lot.stats.available_spaces}/${lot.stats.total_spaces}`}
            onPress={() => handleMarkerPress(lot)}
            pinColor={getMarkerColor(lot)}
          />
        ))}

        {routeCoords.length > 0 && (
          <Polyline coordinates={routeCoords} strokeWidth={4} strokeColor="#0066cc" />
        )}
      </MapView>

      {/* Button to fit all markers */}
      {parkingLots.length > 1 && (
        <TouchableOpacity style={styles.centerButton} onPress={fitMapToMarkers}>
          <Text style={styles.centerButtonText}>📍 View All</Text>
        </TouchableOpacity>
      )}

      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{selectedLot?.name || "Parking Lot"}</Text>
            <Text style={styles.modalAddress}>{selectedLot?.address}</Text>

            {loading ? (
              <ActivityIndicator size="large" color="#0066cc" style={styles.loader} />
            ) : parkingData ? (
              <View style={styles.dataContainer}>
                <View style={styles.statRow}>
                  <Text style={styles.statLabel}>Cars Detected:</Text>
                  <Text style={styles.statValue}>{parkingData.car_count}</Text>
                </View>
                <View style={styles.statRow}>
                  <Text style={styles.statLabel}>Available Spaces:</Text>
                  <Text style={styles.statValueGreen}>{parkingData.available_spaces}</Text>
                </View>
                <View style={styles.statRow}>
                  <Text style={styles.statLabel}>Total Spaces:</Text>
                  <Text style={styles.statValue}>{parkingData.total_spaces}</Text>
                </View>
                <View style={styles.statRow}>
                  <Text style={styles.statLabel}>Occupancy Rate:</Text>
                  <Text style={styles.statValue}>
                    {Math.round((parkingData.car_count / parkingData.total_spaces) * 100)}%
                  </Text>
                </View>
              </View>
            ) : (
              <Text style={styles.loadingText}>Analyzing parking lot...</Text>
            )}

            <TouchableOpacity
              style={[styles.button, styles.navigateButton]}
              onPress={navigateTo}
              disabled={loading}
            >
              <Text style={styles.buttonText}>Navigate to Parking Lot</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.closeButton]}
              onPress={() => setModalVisible(false)}
            >
              <Text style={styles.buttonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { flex: 1 },
  centerButton: {
    position: "absolute",
    top: 50,
    right: 20,
    backgroundColor: "white",
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  centerButtonText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#0066cc",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "white",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    minHeight: 300,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 5,
    textAlign: "center",
    color: "#333",
  },
  modalAddress: {
    fontSize: 14,
    color: "#666",
    textAlign: "center",
    marginBottom: 20,
  },
  loader: {
    marginVertical: 30,
  },
  loadingText: {
    textAlign: "center",
    color: "#666",
    fontSize: 16,
    marginVertical: 30,
  },
  dataContainer: {
    marginBottom: 20,
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  statLabel: {
    fontSize: 16,
    color: "#666",
  },
  statValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
  },
  statValueGreen: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#28a745",
  },
  button: {
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  navigateButton: {
    backgroundColor: "#0066cc",
  },
  closeButton: {
    backgroundColor: "#6c757d",
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600",
  },
});