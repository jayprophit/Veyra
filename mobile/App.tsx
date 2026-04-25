/**
 * Financial Master - React Native Mobile App
 * ============================================
 * Cross-platform iOS/Android application
 * Shared logic with web dashboard
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  useColorScheme,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { Provider as ReduxProvider } from 'react-redux';
import { store } from './src/store';

// Screens
import { PortfolioScreen } from './src/screens/PortfolioScreen';
import { TradingScreen } from './src/screens/TradingScreen';
import { TaxScreen } from './src/screens/TaxScreen';
import { FuelTrackerScreen } from './src/screens/FuelTrackerScreen';
import { DashboardScreen } from './src/screens/DashboardScreen';
import { SettingsScreen } from './src/screens/SettingsScreen';

// Services
import { websocketService } from './src/services/websocket';
import { notificationService } from './src/services/notifications';
import { biometricAuth } from './src/services/biometricAuth';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// Main Tab Navigator
function MainTabs() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
              break;
            case 'Portfolio':
              iconName = focused ? 'chart-pie' : 'chart-pie-outline';
              break;
            case 'Trade':
              iconName = focused ? 'swap-horizontal' : 'swap-horizontal';
              break;
            case 'Fuel':
              iconName = focused ? 'gas-station' : 'gas-station-outline';
              break;
            case 'Tax':
              iconName = focused ? 'calculator' : 'calculator-outline';
              break;
            case 'Settings':
              iconName = focused ? 'cog' : 'cog-outline';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: isDark ? '#888' : '#666',
        tabBarStyle: {
          backgroundColor: isDark ? '#1a1a1a' : '#fff',
          borderTopColor: isDark ? '#333' : '#e0e0e0',
        },
        headerStyle: {
          backgroundColor: isDark ? '#1a1a1a' : '#fff',
        },
        headerTintColor: isDark ? '#fff' : '#000',
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} />
      <Tab.Screen name="Trade" component={TradingScreen} />
      <Tab.Screen name="Fuel" component={FuelTrackerScreen} />
      <Tab.Screen name="Tax" component={TaxScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

// Root App Component
export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize services
      await notificationService.requestPermissions();
      await notificationService.configure();
      
      // Connect to WebSocket for real-time data
      websocketService.connect();
      
      // Check biometric auth availability
      const bioAvailable = await biometricAuth.isAvailable();
      
      setIsLoading(false);
    } catch (error) {
      console.error('App initialization error:', error);
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <StatusBar barStyle="light-content" />
        <Icon name="finance" size={80} color="#2196F3" />
        <Text style={styles.loadingText}>Financial Master</Text>
      </View>
    );
  }

  return (
    <ReduxProvider store={store}>
      <NavigationContainer>
        <StatusBar barStyle="dark-content" />
        <MainTabs />
      </NavigationContainer>
    </ReduxProvider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
});
