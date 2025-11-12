import { IconSymbol } from '@/components/ui/icon-symbol';
import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function ProfileScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Profile</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Settings</Text>
        
        <TouchableOpacity style={styles.menuItem}>
          <IconSymbol name="bell.fill" size={24} color="#0066cc" />
          <Text style={styles.menuText}>Notifications</Text>
          <IconSymbol name="chevron.right" size={20} color="#999" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <IconSymbol name="location.fill" size={24} color="#0066cc" />
          <Text style={styles.menuText}>Location Services</Text>
          <IconSymbol name="chevron.right" size={20} color="#999" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <IconSymbol name="moon.fill" size={24} color="#0066cc" />
          <Text style={styles.menuText}>Dark Mode</Text>
          <IconSymbol name="chevron.right" size={20} color="#999" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <TouchableOpacity style={styles.menuItem}>
          <IconSymbol name="info.circle.fill" size={24} color="#0066cc" />
          <Text style={styles.menuText}>App Version</Text>
          <Text style={styles.versionText}>1.0.0</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <IconSymbol name="questionmark.circle.fill" size={24} color="#0066cc" />
          <Text style={styles.menuText}>Help & Support</Text>
          <IconSymbol name="chevron.right" size={20} color="#999" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  section: {
    marginTop: 20,
    backgroundColor: 'white',
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    paddingVertical: 15,
    textTransform: 'uppercase',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  menuText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    marginLeft: 15,
  },
  versionText: {
    fontSize: 14,
    color: '#999',
  },
});