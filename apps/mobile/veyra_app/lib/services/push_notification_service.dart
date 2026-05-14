import 'dart:async';
import 'dart:io';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:logger/logger.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';

class PushNotificationService {
  static final PushNotificationService _instance = PushNotificationService._internal();
  factory PushNotificationService() => _instance;
  PushNotificationService._internal();

  final Logger _logger = Logger();
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final Dio _dio = Dio();

  // Notification streams
  final StreamController<RemoteMessage> _messageStreamController = StreamController<RemoteMessage>.broadcast();
  final StreamController<String> _tokenStreamController = StreamController<String>.broadcast();

  Stream<RemoteMessage> get messageStream => _messageStreamController.stream;
  Stream<String> get tokenStream => _tokenStreamController.stream;

  // Initialize notifications
  Future<void> initialize() async {
    try {
      // Request permission
      await _requestPermissions();

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Initialize Firebase messaging
      await _initializeFirebaseMessaging();

      // Get initial message
      final RemoteMessage? initialMessage = await _firebaseMessaging.getInitialMessage();
      if (initialMessage != null) {
        _handleMessage(initialMessage);
      }

      _logger.i('Push notification service initialized');
    } catch (e) {
      _logger.e('Error initializing push notifications: $e');
    }
  }

  // Request notification permissions
  Future<bool> _requestPermissions() async {
    if (Platform.isIOS) {
      final settings = await _firebaseMessaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );
      return settings.authorizationStatus == AuthorizationStatus.authorized;
    } else if (Platform.isAndroid) {
      final AndroidNotificationChannel channel = AndroidNotificationChannel(
        'high_importance_channel',
        'High Importance Notifications',
        description: 'This channel is used for important notifications.',
        importance: Importance.high,
      );

      await _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);

      return true;
    }
    return false;
  }

  // Initialize local notifications
  Future<void> _initializeLocalNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );

    await _localNotifications.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }

  // Initialize Firebase messaging
  Future<void> _initializeFirebaseMessaging() async {
    // Get token
    final String? token = await _firebaseMessaging.getToken();
    if (token != null) {
      await _saveToken(token);
      _tokenStreamController.add(token);
    }

    // Listen for token refresh
    _firebaseMessaging.onTokenRefresh.listen((token) async {
      await _saveToken(token);
      _tokenStreamController.add(token);
    });

    // Listen for foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Listen for background messages
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Listen for message taps when app is opened from notification
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessage);
  }

  // Save token to secure storage and server
  Future<void> _saveToken(String token) async {
    try {
      await _secureStorage.write(key: 'fcm_token', value: token);
      
      // Send token to server
      await _sendTokenToServer(token);
      
      _logger.i('FCM token saved: ${token.substring(0, 8)}...');
    } catch (e) {
      _logger.e('Error saving token: $e');
    }
  }

  // Send token to server
  Future<void> _sendTokenToServer(String token) async {
    try {
      final response = await _dio.post(
        'https://api.veyra.com/v1/notifications/register',
        data: {
          'token': token,
          'platform': Platform.operatingSystem,
          'version': '1.0.0',
        },
      );

      if (response.statusCode == 200) {
        _logger.i('Token registered with server');
      }
    } catch (e) {
      _logger.e('Error registering token with server: $e');
    }
  }

  // Handle foreground messages
  Future<void> _handleForegroundMessage(RemoteMessage message) async {
    _logger.i('Received foreground message: ${message.notification?.title}');
    
    // Show local notification
    await _showLocalNotification(message);
    
    // Add to stream for UI to handle
    _messageStreamController.add(message);
  }

  // Handle background messages
  static Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
    final logger = Logger();
    logger.i('Handling background message: ${message.notification?.title}');
    // Handle background message logic here
  }

  // Handle message when app is opened from notification
  void _handleMessage(RemoteMessage message) {
    _logger.i('App opened from notification: ${message.notification?.title}');
    _messageStreamController.add(message);
  }

  // Show local notification
  Future<void> _showLocalNotification(RemoteMessage message) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'high_importance_channel',
      'High Importance Notifications',
      channelDescription: 'This channel is used for important notifications.',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );

    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );

    await _localNotifications.show(
      message.hashCode,
      message.notification?.title ?? 'Veyra',
      message.notification?.body ?? 'New notification',
      platformChannelSpecifics,
      payload: message.data.toString(),
    );
  }

  // Handle notification tap
  void _onNotificationTapped(NotificationResponse response) {
    _logger.i('Notification tapped: ${response.payload}');
    // Handle navigation based on notification payload
    _handleNotificationNavigation(response.payload);
  }

  // Handle navigation from notification
  void _handleNotificationNavigation(String? payload) {
    if (payload != null) {
      try {
        final data = Map<String, dynamic>.from(
          // Parse payload and navigate accordingly
          // This would integrate with your navigation system
        );
        _logger.d('Navigating to: $data');
      } catch (e) {
        _logger.e('Error parsing notification payload: $e');
      }
    }
  }

  // Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _firebaseMessaging.subscribeToTopic(topic);
      _logger.i('Subscribed to topic: $topic');
    } catch (e) {
      _logger.e('Error subscribing to topic: $e');
    }
  }

  // Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _firebaseMessaging.unsubscribeFromTopic(topic);
      _logger.i('Unsubscribed from topic: $topic');
    } catch (e) {
      _logger.e('Error unsubscribing from topic: $e');
    }
  }

  // Send local notification
  Future<void> sendLocalNotification({
    required String title,
    required String body,
    String? payload,
    String channelId = 'high_importance_channel',
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'high_importance_channel',
      'High Importance Notifications',
      channelDescription: 'This channel is used for important notifications.',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );

    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );

    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch.remainder(100000),
      title,
      body,
      platformChannelSpecifics,
      payload: payload,
    );
  }

  // Get current token
  Future<String?> getCurrentToken() async {
    try {
      return await _firebaseMessaging.getToken();
    } catch (e) {
      _logger.e('Error getting current token: $e');
      return null;
    }
  }

  // Check if notifications are enabled
  Future<bool> areNotificationsEnabled() async {
    if (Platform.isIOS) {
      final settings = await _firebaseMessaging.getNotificationSettings();
      return settings.authorizationStatus == AuthorizationStatus.authorized;
    }
    return true; // Android permissions are handled at app install
  }

  // Clear all notifications
  Future<void> clearAllNotifications() async {
    await _localNotifications.cancelAll();
    _logger.i('All notifications cleared');
  }

  // Dispose
  void dispose() {
    _messageStreamController.close();
    _tokenStreamController.close();
  }
}

// Notification types for Veyra
enum NotificationType {
  priceAlert,
  tradeExecution,
  portfolioUpdate,
  marketNews,
  systemAlert,
  accountUpdate,
}

class VeyraNotification {
  final String id;
  final NotificationType type;
  final String title;
  final String body;
  final Map<String, dynamic>? data;
  final DateTime timestamp;
  final bool read;

  VeyraNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    this.data,
    required this.timestamp,
    this.read = false,
  });

  factory VeyraNotification.fromRemoteMessage(RemoteMessage message) {
    final type = _parseNotificationType(message.data['type'] ?? 'systemAlert');
    
    return VeyraNotification(
      id: message.messageId ?? '',
      type: type,
      title: message.notification?.title ?? 'Veyra',
      body: message.notification?.body ?? '',
      data: message.data,
      timestamp: message.sentTime ?? DateTime.now(),
      read: false,
    );
  }

  static NotificationType _parseNotificationType(String typeString) {
    switch (typeString) {
      case 'priceAlert':
        return NotificationType.priceAlert;
      case 'tradeExecution':
        return NotificationType.tradeExecution;
      case 'portfolioUpdate':
        return NotificationType.portfolioUpdate;
      case 'marketNews':
        return NotificationType.marketNews;
      case 'systemAlert':
        return NotificationType.systemAlert;
      case 'accountUpdate':
        return NotificationType.accountUpdate;
      default:
        return NotificationType.systemAlert;
    }
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'type': type.toString(),
      'title': title,
      'body': body,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
      'read': read,
    };
  }
}
