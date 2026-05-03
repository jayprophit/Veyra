import { useCallback, useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  payload: unknown;
  timestamp?: number;
}

interface WebSocketHookOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (data: WebSocketMessage) => void;
}

interface WebSocketHookReturn {
  connected: boolean;
  connect: () => void;
  disconnect: () => void;
  send: (type: string, payload: unknown) => boolean;
  alerts: string[];
  lastMessage: WebSocketMessage | null;
}

export function useEnhancedWebSocket(options: WebSocketHookOptions): WebSocketHookReturn {
  const {
    url,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10,
    onOpen,
    onClose,
    onError,
    onMessage,
  } = options;

  const [connected, setConnected] = useState(false);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  }, []);

  const disconnect = useCallback(() => {
    clearReconnectTimer();
    reconnectAttemptsRef.current = maxReconnectAttempts;

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, [clearReconnectTimer, maxReconnectAttempts]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onclose = () => {
        setConnected(false);
        onClose?.();

        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        onError?.(error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(data);

          if (data.type === 'alert') {
            setAlerts(prev => [...prev.slice(-4), data.payload as string]);
          }

          onMessage?.(data);
        } catch {
          console.error('Failed to parse WebSocket message');
        }
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [url, reconnectInterval, maxReconnectAttempts, onOpen, onClose, onError, onMessage, clearReconnectTimer]);

  const send = useCallback((type: string, payload: unknown): boolean => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return false;
    }

    try {
      wsRef.current.send(JSON.stringify({
        type,
        payload,
        timestamp: Date.now(),
      }));
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearReconnectTimer();
      wsRef.current?.close();
    };
  }, [connect, clearReconnectTimer]);

  return {
    connected,
    connect,
    disconnect,
    send,
    alerts,
    lastMessage,
  };
}

// Bridge pattern for external data sources (from DataSphere)
interface OSAgentSource {
  key: string;
  name: string;
  icon: string;
  description: string;
}

export const OS_AGENT_SOURCES: Record<string, OSAgentSource> = {
  'local-files': {
    key: 'local-files',
    name: 'Local Files',
    icon: '📁',
    description: 'Import CSV, JSON, Excel files from your computer',
  },
  'clipboard': {
    key: 'clipboard',
    name: 'Clipboard',
    icon: '📋',
    description: 'Paste data directly from clipboard',
  },
  'browser': {
    key: 'browser',
    name: 'Browser Storage',
    icon: '🌐',
    description: 'Import from browser localStorage or IndexedDB',
  },
  'api': {
    key: 'api',
    name: 'External API',
    icon: '🔌',
    description: 'Connect to external REST API endpoints',
  },
};

export function useOSAgentBridge() {
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback((port: number = 47291) => {
    try {
      const ws = new WebSocket(`ws://localhost:${port}`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onerror = () => setConnected(false);
    } catch {
      setConnected(false);
    }
  }, []);

  const scrapeSource = useCallback((sourceKey: string, options?: Record<string, unknown>) => {
    if (!connected || !wsRef.current) {
      console.warn('OS Agent not connected');
      return false;
    }

    wsRef.current.send(JSON.stringify({
      type: 'scrape',
      payload: { source: sourceKey, options: options || {} },
    }));
    return true;
  }, [connected]);

  return {
    connected,
    connect,
    scrapeSource,
    sources: OS_AGENT_SOURCES,
  };
}
