import 'dart:convert';
import 'dart:async';
import 'package:hive/hive.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:logger/logger.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class OfflineSyncService {
  static final OfflineSyncService _instance = OfflineSyncService._internal();
  factory OfflineSyncService() => _instance;
  OfflineSyncService._internal();

  final Logger _logger = Logger();
  late Box _offlineBox;
  late Box _syncQueueBox;
  WebSocketChannel? _wsChannel;
  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  Timer? _syncTimer;
  bool _isOnline = true;
  bool _isSyncing = false;

  // Initialize offline storage
  Future<void> initialize() async {
    try {
      // Register Hive adapters if needed
      if (!Hive.isAdapterRegistered(0)) {
        Hive.registerAdapter(OfflineDataAdapter());
      }
      
      _offlineBox = await Hive.openBox('offline_data');
      _syncQueueBox = await Hive.openBox('sync_queue');
      
      // Monitor connectivity
      _connectivitySubscription = Connectivity().onConnectivityChanged.listen(_onConnectivityChanged);
      
      // Start periodic sync
      _startPeriodicSync();
      
      // Check initial connectivity
      final connectivityResult = await Connectivity().checkConnectivity();
      _isOnline = connectivityResult != ConnectivityResult.none;
      
      _logger.i('Offline sync service initialized');
    } catch (e) {
      _logger.e('Error initializing offline sync: $e');
    }
  }

  // Handle connectivity changes
  void _onConnectivityChanged(ConnectivityResult result) {
    final wasOffline = !_isOnline;
    _isOnline = result != ConnectivityResult.none;
    
    if (wasOffline && _isOnline) {
      _logger.i('Connection restored, starting sync');
      _syncAllPendingData();
    } else if (!_isOnline) {
      _logger.i('Connection lost, entering offline mode');
    }
  }

  // Store data locally when offline
  Future<void> storeOfflineData(String key, dynamic data, {String? endpoint}) async {
    try {
      final offlineData = OfflineData(
        key: key,
        data: data,
        timestamp: DateTime.now(),
        endpoint: endpoint,
        synced: _isOnline,
      );
      
      await _offlineBox.put(key, offlineData);
      
      if (!_isOnline && endpoint != null) {
        // Add to sync queue
        await _addToSyncQueue(key, endpoint, 'POST');
      }
      
      _logger.d('Stored offline data: $key');
    } catch (e) {
      _logger.e('Error storing offline data: $e');
    }
  }

  // Get offline data
  Future<T?> getOfflineData<T>(String key) async {
    try {
      final offlineData = _offlineBox.get(key) as OfflineData?;
      if (offlineData != null) {
        return offlineData.data as T?;
      }
      return null;
    } catch (e) {
      _logger.e('Error getting offline data: $e');
      return null;
    }
  }

  // Add operation to sync queue
  Future<void> _addToSyncQueue(String key, String endpoint, String method) async {
    try {
      final syncOperation = SyncOperation(
        key: key,
        endpoint: endpoint,
        method: method,
        timestamp: DateTime.now(),
        retryCount: 0,
      );
      
      await _syncQueueBox.add(syncOperation);
      _logger.d('Added to sync queue: $endpoint');
    } catch (e) {
      _logger.e('Error adding to sync queue: $e');
    }
  }

  // Sync all pending data
  Future<void> _syncAllPendingData() async {
    if (_isSyncing || !_isOnline) return;
    
    _isSyncing = true;
    
    try {
      final operations = _syncQueueBox.values.toList().cast<SyncOperation>();
      
      for (final operation in operations) {
        await _syncOperation(operation);
      }
      
      _logger.i('Sync completed: ${operations.length} operations');
    } catch (e) {
      _logger.e('Error during sync: $e');
    } finally {
      _isSyncing = false;
    }
  }

  // Sync individual operation
  Future<void> _syncOperation(SyncOperation operation) async {
    try {
      final offlineData = _offlineBox.get(operation.key) as OfflineData?;
      if (offlineData == null) {
        await _syncQueueBox.delete(operation.key);
        return;
      }

      // Attempt to sync with server
      final success = await _sendToServer(operation.endpoint, offlineData.data);
      
      if (success) {
        // Mark as synced and remove from queue
        offlineData.synced = true;
        await _offlineBox.put(operation.key, offlineData);
        await _syncQueueBox.delete(operation.key);
        
        _logger.d('Synced successfully: ${operation.endpoint}');
      } else {
        // Increment retry count
        operation.retryCount++;
        if (operation.retryCount >= 3) {
          // Max retries reached, remove from queue
          await _syncQueueBox.delete(operation.key);
          _logger.w('Max retries reached for: ${operation.endpoint}');
        } else {
          await _syncQueueBox.put(operation.key, operation);
        }
      }
    } catch (e) {
      _logger.e('Error syncing operation: $e');
    }
  }

  // Send data to server
  Future<bool> _sendToServer(String endpoint, dynamic data) async {
    try {
      // This would integrate with your existing API service
      // For now, simulate a successful sync
      await Future.delayed(Duration(milliseconds: 500));
      
      _logger.d('Data sent to server: $endpoint');
      return true;
    } catch (e) {
      _logger.e('Error sending to server: $e');
      return false;
    }
  }

  // Start periodic sync
  void _startPeriodicSync() {
    _syncTimer = Timer.periodic(Duration(minutes: 5), (timer) {
      if (_isOnline && !_isSyncing) {
        _syncAllPendingData();
      }
    });
  }

  // Get sync status
  SyncStatus getSyncStatus() {
    final pendingOperations = _syncQueueBox.length;
    final totalOfflineData = _offlineBox.length;
    
    return SyncStatus(
      isOnline: _isOnline,
      isSyncing: _isSyncing,
      pendingOperations: pendingOperations,
      totalOfflineData: totalOfflineData,
      lastSyncTime: DateTime.now(),
    );
  }

  // Force sync
  Future<void> forceSync() async {
    if (_isOnline) {
      await _syncAllPendingData();
    }
  }

  // Clear all offline data
  Future<void> clearOfflineData() async {
    try {
      await _offlineBox.clear();
      await _syncQueueBox.clear();
      _logger.i('Offline data cleared');
    } catch (e) {
      _logger.e('Error clearing offline data: $e');
    }
  }

  // Dispose
  void dispose() {
    _syncTimer?.cancel();
    _connectivitySubscription?.cancel();
    _wsChannel?.sink.close();
  }
}

// Models for offline data
class OfflineData {
  final String key;
  final dynamic data;
  final DateTime timestamp;
  final String? endpoint;
  bool synced;

  OfflineData({
    required this.key,
    required this.data,
    required this.timestamp,
    this.endpoint,
    this.synced = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'key': key,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
      'endpoint': endpoint,
      'synced': synced,
    };
  }

  factory OfflineData.fromMap(Map<String, dynamic> map) {
    return OfflineData(
      key: map['key'],
      data: map['data'],
      timestamp: DateTime.parse(map['timestamp']),
      endpoint: map['endpoint'],
      synced: map['synced'] ?? false,
    );
  }
}

class SyncOperation {
  final String key;
  final String endpoint;
  final String method;
  final DateTime timestamp;
  int retryCount;

  SyncOperation({
    required this.key,
    required this.endpoint,
    required this.method,
    required this.timestamp,
    this.retryCount = 0,
  });

  Map<String, dynamic> toMap() {
    return {
      'key': key,
      'endpoint': endpoint,
      'method': method,
      'timestamp': timestamp.toIso8601String(),
      'retryCount': retryCount,
    };
  }

  factory SyncOperation.fromMap(Map<String, dynamic> map) {
    return SyncOperation(
      key: map['key'],
      endpoint: map['endpoint'],
      method: map['method'],
      timestamp: DateTime.parse(map['timestamp']),
      retryCount: map['retryCount'] ?? 0,
    );
  }
}

class SyncStatus {
  final bool isOnline;
  final bool isSyncing;
  final int pendingOperations;
  final int totalOfflineData;
  final DateTime lastSyncTime;

  SyncStatus({
    required this.isOnline,
    required this.isSyncing,
    required this.pendingOperations,
    required this.totalOfflineData,
    required this.lastSyncTime,
  });
}

// Hive adapter for OfflineData
class OfflineDataAdapter extends TypeAdapter<OfflineData> {
  @override
  final typeId = 0;

  @override
  OfflineData read(BinaryReader reader) {
    return OfflineData.fromMap(reader.readMap());
  }

  @override
  void write(BinaryWriter writer, OfflineData obj) {
    writer.writeMap(obj.toMap());
  }
}
