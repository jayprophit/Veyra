/**
 * Veyra - React Native Mobile App
 * 
 * Features:
 * - Trading dashboard
 * - Portfolio management
 * - Voice commands
 * - Push notifications
 * - Biometric auth
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  StatusBar,
  Alert,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
const DashboardScreen = () => {
  const [portfolioValue, setPortfolioValue] = useState(125432.56);
  const [dailyChange, setDailyChange] = useState(2.34);
  const [activeBots, setActiveBots] = useState(3);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Veyra</Text>
        <TouchableOpacity style={styles.voiceButton}>
          <Icon name="microphone" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <View style={styles.portfolioCard}>
        <Text style={styles.portfolioLabel}>Portfolio Value</Text>
        <Text style={styles.portfolioValue}>
          ${portfolioValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </Text>
        <View style={styles.changeContainer}>
          <Icon 
            name={dailyChange >= 0 ? "trending-up" : "trending-down"} 
            size={20} 
            color={dailyChange >= 0 ? "#4CAF50" : "#f44336"} 
          />
          <Text style={[styles.changeText, { color: dailyChange >= 0 ? "#4CAF50" : "#f44336" }]}>
            {dailyChange >= 0 ? '+' : ''}{dailyChange}%
          </Text>
        </View>
      </View>

      <View style={styles.statsGrid}>
        <View style={styles.statCard}>
          <Icon name="robot" size={28} color="#6200ee" />
          <Text style={styles.statValue}>{activeBots}</Text>
          <Text style={styles.statLabel}>Active Bots</Text>
        </View>
        <View style={styles.statCard}>
          <Icon name="chart-line" size={28} color="#6200ee" />
          <Text style={styles.statValue}>24</Text>
          <Text style={styles.statLabel}>Today's Trades</Text>
        </View>
        <View style={styles.statCard}>
          <Icon name="trophy" size={28} color="#6200ee" />
          <Text style={styles.statValue}>Lvl 12</Text>
          <Text style={styles.statLabel}>Level</Text>
        </View>
        <View style={styles.statCard}>
          <Icon name="fire" size={28} color="#6200ee" />
          <Text style={styles.statValue}>15</Text>
          <Text style={styles.statLabel}>Day Streak</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Quick Actions</Text>
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="plus-circle" size={32} color="#6200ee" />
          <Text style={styles.actionText}>New Trade</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="robot" size={32} color="#6200ee" />
          <Text style={styles.actionText}>Start Bot</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="chart-pie" size={32} color="#6200ee" />
          <Text style={styles.actionText}>Portfolio</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="bell" size={32} color="#6200ee" />
          <Text style={styles.actionText}>Alerts</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.sectionTitle}>Market Overview</Text>
      <View style={styles.marketList}>
        {['BTC/USD', 'ETH/USD', 'EUR/USD', 'AAPL'].map((symbol) => (
          <View key={symbol} style={styles.marketItem}>
            <View style={styles.marketSymbol}>
              <Text style={styles.symbolText}>{symbol}</Text>
            </View>
            <View style={styles.marketPrice}>
              <Text style={styles.priceText}>$42,345.67</Text>
              <Text style={styles.changePositive}>+1.23%</Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
};

const TradingScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Trading</Text>
    <View style={styles.comingSoon}>
      <Icon name="chart-candlestick" size={64} color="#6200ee" />
      <Text style={styles.comingSoonText}>Advanced Trading Interface</Text>
    </View>
  </View>
);

const SocialScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Social Feed</Text>
    <ScrollView>
      {[1, 2, 3].map((i) => (
        <View key={i} style={styles.feedItem}>
          <View style={styles.feedHeader}>
            <View style={styles.avatar}>
              <Icon name="account" size={24} color="#fff" />
            </View>
            <View>
              <Text style={styles.feedUser}>Trader_{i}</Text>
              <Text style={styles.feedTime}>2h ago</Text>
            </View>
          </View>
          <Text style={styles.feedContent}>
            Just executed a successful BTC long! +5.2% profit 🚀
          </Text>
          <View style={styles.feedActions}>
            <TouchableOpacity style={styles.feedAction}>
              <Icon name="heart-outline" size={20} color="#666" />
              <Text style={styles.feedActionText}>24</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.feedAction}>
              <Icon name="comment-outline" size={20} color="#666" />
              <Text style={styles.feedActionText}>5</Text>
            </TouchableOpacity>
          </View>
        </View>
      ))}
    </ScrollView>
  </View>
);

const ProfileScreen = () => (
  <View style={styles.container}>
    <Text style={styles.title}>Profile</Text>
    <View style={styles.profileCard}>
      <View style={styles.profileAvatar}>
        <Icon name="account" size={48} color="#fff" />
      </View>
      <Text style={styles.profileName}>Your Profile</Text>
      <Text style={styles.profileLevel}>Level 12 • 15 Day Streak 🔥</Text>
    </View>
    <View style={styles.settingsList}>
      <TouchableOpacity style={styles.settingItem}>
        <Icon name="face-recognition" size={24} color="#6200ee" />
        <Text style={styles.settingText}>Face Recognition Auth</Text>
        <Icon name="chevron-right" size={24} color="#666" />
      </TouchableOpacity>
      <TouchableOpacity style={styles.settingItem}>
        <Icon name="fingerprint" size={24} color="#6200ee" />
        <Text style={styles.settingText}>Biometric Login</Text>
        <Icon name="chevron-right" size={24} color="#666" />
      </TouchableOpacity>
      <TouchableOpacity style={styles.settingItem}>
        <Icon name="bell" size={24} color="#6200ee" />
        <Text style={styles.settingText}>Notifications</Text>
        <Icon name="chevron-right" size={24} color="#666" />
      </TouchableOpacity>
      <TouchableOpacity style={styles.settingItem}>
        <Icon name="shield-check" size={24} color="#6200ee" />
        <Text style={styles.settingText}>Security</Text>
        <Icon name="chevron-right" size={24} color="#666" />
      </TouchableOpacity>
    </View>
  </View>
);

// Navigation Setup
const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const TabNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName: string;
        switch (route.name) {
          case 'Dashboard':
            iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
            break;
          case 'Trading':
            iconName = focused ? 'chart-line' : 'chart-line';
            break;
          case 'Social':
            iconName = focused ? 'account-group' : 'account-group-outline';
            break;
          case 'Profile':
            iconName = focused ? 'account' : 'account-outline';
            break;
          default:
            iconName = 'help';
        }
        return <Icon name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#6200ee',
      tabBarInactiveTintColor: '#666',
      headerShown: false,
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} />
    <Tab.Screen name="Trading" component={TradingScreen} />
    <Tab.Screen name="Social" component={SocialScreen} />
    <Tab.Screen name="Profile" component={ProfileScreen} />
  </Tab.Navigator>
);

const App = () => {
  return (
    <NavigationContainer>
      <StatusBar barStyle="light-content" backgroundColor="#6200ee" />
      <SafeAreaView style={styles.safeArea}>
        <TabNavigator />
      </SafeAreaView>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#6200ee',
  },
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#6200ee',
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  voiceButton: {
    padding: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 20,
  },
  portfolioCard: {
    backgroundColor: '#6200ee',
    margin: 16,
    padding: 24,
    borderRadius: 16,
    elevation: 4,
  },
  portfolioLabel: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
  },
  portfolioValue: {
    color: '#fff',
    fontSize: 36,
    fontWeight: 'bold',
    marginTop: 8,
  },
  changeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  changeText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 4,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
  },
  statCard: {
    width: '50%',
    padding: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginHorizontal: 16,
    marginTop: 24,
    marginBottom: 12,
    color: '#333',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 16,
  },
  actionButton: {
    alignItems: 'center',
    padding: 12,
  },
  actionText: {
    marginTop: 8,
    fontSize: 12,
    color: '#666',
  },
  marketList: {
    paddingHorizontal: 16,
  },
  marketItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  marketSymbol: {
    justifyContent: 'center',
  },
  symbolText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  marketPrice: {
    alignItems: 'flex-end',
  },
  priceText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  changePositive: {
    fontSize: 14,
    color: '#4CAF50',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    margin: 16,
    color: '#333',
  },
  comingSoon: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  comingSoonText: {
    fontSize: 18,
    color: '#666',
    marginTop: 16,
  },
  feedItem: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 12,
    elevation: 2,
  },
  feedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#6200ee',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  feedUser: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  feedTime: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  feedContent: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  feedActions: {
    flexDirection: 'row',
    marginTop: 12,
  },
  feedAction: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  feedActionText: {
    marginLeft: 4,
    color: '#666',
    fontSize: 14,
  },
  profileCard: {
    backgroundColor: '#6200ee',
    margin: 16,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  profileAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  profileName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginTop: 16,
  },
  profileLevel: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
    marginTop: 8,
  },
  settingsList: {
    marginTop: 16,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 8,
    borderRadius: 12,
  },
  settingText: {
    flex: 1,
    fontSize: 16,
    marginLeft: 16,
    color: '#333',
  },
});

export default App;
