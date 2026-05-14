import 'package:local_auth/local_auth.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';

class BiometricAuthService {
  static final BiometricAuthService _instance = BiometricAuthService._internal();
  factory BiometricAuthService() => _instance;
  BiometricAuthService._internal();

  final LocalAuthentication _auth = LocalAuthentication();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final Logger _logger = Logger();

  // Check if device supports biometric authentication
  Future<bool> isDeviceSupported() async {
    try {
      final bool canAuthenticateWithBiometrics = await _auth.canCheckBiometrics;
      final bool canAuthenticate = await _auth.isDeviceSupported();
      return canAuthenticateWithBiometrics && canAuthenticate;
    } catch (e) {
      _logger.e('Error checking biometric support: $e');
      return false;
    }
  }

  // Get available biometric types
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (e) {
      _logger.e('Error getting available biometrics: $e');
      return [];
    }
  }

  // Authenticate with biometrics
  Future<bool> authenticate({
    String reason = 'Authenticate to access Veyra',
    bool useErrorDialogs = true,
    bool stickyAuth = true,
    bool biometricOnly = false,
  }) async {
    try {
      final bool authenticated = await _auth.authenticate(
        localizedReason: reason,
        useErrorDialogs: useErrorDialogs,
        stickyAuth: stickyAuth,
        biometricOnly: biometricOnly,
      );
      
      if (authenticated) {
        await _secureStorage.write(
          key: 'biometric_enabled',
          value: 'true',
        );
      }
      
      return authenticated;
    } catch (e) {
      _logger.e('Biometric authentication failed: $e');
      return false;
    }
  }

  // Enable biometric authentication
  Future<bool> enableBiometric() async {
    try {
      final bool isSupported = await isDeviceSupported();
      if (!isSupported) {
        return false;
      }

      final bool authenticated = await authenticate(
        reason: 'Enable biometric authentication for quick access',
      );

      if (authenticated) {
        await _secureStorage.write(
          key: 'biometric_enabled',
          value: 'true',
        );
        _logger.i('Biometric authentication enabled');
        return true;
      }
      return false;
    } catch (e) {
      _logger.e('Error enabling biometric: $e');
      return false;
    }
  }

  // Disable biometric authentication
  Future<void> disableBiometric() async {
    try {
      await _secureStorage.delete(key: 'biometric_enabled');
      _logger.i('Biometric authentication disabled');
    } catch (e) {
      _logger.e('Error disabling biometric: $e');
    }
  }

  // Check if biometric is enabled
  Future<bool> isBiometricEnabled() async {
    try {
      final String? value = await _secureStorage.read(key: 'biometric_enabled');
      return value == 'true';
    } catch (e) {
      _logger.e('Error checking biometric status: $e');
      return false;
    }
  }

  // Auto-authenticate if biometric is enabled
  Future<bool> autoAuthenticate() async {
    try {
      final bool isEnabled = await isBiometricEnabled();
      if (isEnabled) {
        return await authenticate(
          reason: 'Quick access to Veyra',
          biometricOnly: true,
        );
      }
      return false;
    } catch (e) {
      _logger.e('Error in auto-authentication: $e');
      return false;
    }
  }

  // Get biometric type name for UI
  String getBiometricTypeName(BiometricType type) {
    switch (type) {
      case BiometricType.fingerprint:
        return 'Fingerprint';
      case BiometricType.face:
        return 'Face ID';
      case BiometricType.iris:
        return 'Iris Scanner';
      case BiometricType.weak:
        return 'Device PIN/Pattern';
      case BiometricType.strong:
        return 'Strong Biometric';
      default:
        return 'Unknown';
    }
  }

  // Get biometric icon name
  String getBiometricIcon(BiometricType type) {
    switch (type) {
      case BiometricType.fingerprint:
        return 'fingerprint';
      case BiometricType.face:
        return 'face';
      case BiometricType.iris:
        return 'visibility';
      case BiometricType.weak:
        return 'lock';
      case BiometricType.strong:
        return 'security';
      default:
        return 'help_outline';
    }
  }
}
