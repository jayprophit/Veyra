/**
 * Financial Master Mobile App
 * Main entry point
 */

import React, {useEffect} from 'react';
import {Provider} from 'react-redux';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createStackNavigator} from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {store} from './src/store';
import {useAppSelector, useAppDispatch} from './src/hooks';
import {initializeAuth} from './src/store/slices/authSlice';

// Screens
import DashboardScreen from './src/screens/DashboardScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import TaxScreen from './src/screens/TaxScreen';
import FuelTrackerScreen from './src/screens/FuelTrackerScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import LoginScreen from './src/screens/LoginScreen';
import BiometricPrompt from './src/components/BiometricPrompt';

// Services
import {initializeNotifications} from './src/services/notifications';
import {initializeBackgroundSync} from './src/services/backgroundSync';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Main Tab Navigator
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        tabBarIcon: ({focused, color, size}) => {
          let iconName: string;

          switch (route.name) {
            case 'Dashboard':
              iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
              break;
            case 'Portfolio':
              iconName = focused ? 'chart-pie' : 'chart-pie-outline';
              break;
            case 'Tax':
              iconName = focused ? 'file-document' : 'file-document-outline';
              break;
            case 'Fuel':
              iconName = focused ? 'car' : 'car-outline';
              break;
            case 'Settings':
              iconName = focused ? 'cog' : 'cog-outline';
              break;
            default:
              iconName = 'circle';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#10B981',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#1F2937',
        },
        headerTintColor: '#fff',
        tabBarStyle: {
          backgroundColor: '#1F2937',
          borderTopColor: '#374151',
        },
      })}>
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{title: 'Overview'}}
      />
      <Tab.Screen
        name="Portfolio"
        component={PortfolioScreen}
        options={{title: 'Portfolio'}}
      />
      <Tab.Screen
        name="Tax"
        component={TaxScreen}
        options={{title: 'Tax'}}
      />
      <Tab.Screen
        name="Fuel"
        component={FuelTrackerScreen}
        options={{title: 'Fuel & Mileage'}}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{title: 'Settings'}}
      />
    </Tab.Navigator>
  );
}

// Auth Navigator
function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: {backgroundColor: '#111827'},
      }}>
      <Stack.Screen name="Login" component={LoginScreen} />
    </Stack.Navigator>
  );
}

// Root Navigator with Auth Check
function RootNavigator() {
  const dispatch = useAppDispatch();
  const {isAuthenticated, isLoading, requireBiometric} = useAppSelector(
    state => state.auth,
  );

  useEffect(() => {
    // Initialize auth state
    dispatch(initializeAuth());
    
    // Initialize services
    initializeNotifications();
    initializeBackgroundSync();
  }, [dispatch]);

  if (isLoading) {
    return null; // Or splash screen
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? (
        <>
          <MainTabs />
          {requireBiometric && <BiometricPrompt />}
        </>
      ) : (
        <AuthNavigator />
      )}
    </NavigationContainer>
  );
}

// Main App Component
export default function App(): React.JSX.Element {
  return (
    <Provider store={store}>
      <RootNavigator />
    </Provider>
  );
}
