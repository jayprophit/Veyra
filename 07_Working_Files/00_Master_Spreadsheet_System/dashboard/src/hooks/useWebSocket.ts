"""
React Hook: useWebSocket
=======================
Manages WebSocket connection with automatic reconnection.
"""

import { useState, useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data: any;
  user_id?: string;
}

interface UseWebSocketOptions {
  url: string;
  autoReconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

interface UseWebSocketReturn {
  sendMessage: (message: object) => void;
  subscribe: (symbols: string[]) => void;
  unsubscribe: (symbols: string[]) => void;
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting';
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    url,
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onMessage,
    onConnect,
    onDisconnect,
    onError
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'reconnecting'>('connecting');
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null);
  const subscribedSymbolsRef = useRef<string[]>([]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptsRef.current = 0;
        
        // Resubscribe to previous symbols
        if (subscribedSymbolsRef.current.length > 0) {
          ws.send(JSON.stringify({
            type: 'subscribe',
            symbols: subscribedSymbolsRef.current
          }));
        }
        
        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);
          onMessage?.(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        onDisconnect?.();

        // Auto reconnect
        if (autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          setConnectionStatus('reconnecting');
          reconnectAttemptsRef.current += 1;
          
          console.log(`Reconnecting... Attempt ${reconnectAttemptsRef.current}`);
          
          reconnectTimerRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionStatus('disconnected');
    }
  }, [url, autoReconnect, reconnectInterval, maxReconnectAttempts, onConnect, onDisconnect, onError, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }, []);

  const subscribe = useCallback((symbols: string[]) => {
    subscribedSymbolsRef.current = [...new Set([...subscribedSymbolsRef.current, ...symbols])];
    
    sendMessage({
      type: 'subscribe',
      symbols
    });
  }, [sendMessage]);

  const unsubscribe = useCallback((symbols: string[]) => {
    subscribedSymbolsRef.current = subscribedSymbolsRef.current.filter(s => !symbols.includes(s));
    
    sendMessage({
      type: 'unsubscribe',
      symbols
    });
  }, [sendMessage]);

  // Connect on mount
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Ping to keep connection alive
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      sendMessage({ type: 'ping' });
    }, 30000);

    return () => clearInterval(pingInterval);
  }, [isConnected, sendMessage]);

  return {
    sendMessage,
    subscribe,
    unsubscribe,
    isConnected,
    lastMessage,
    connectionStatus
  };
}


// Hook for price updates only
export function usePriceUpdates(symbols: string[]) {
  const [prices, setPrices] = useState<Record<string, { price: number; change: number; timestamp: string }>>({});

  const { subscribe, unsubscribe, isConnected } = useWebSocket({
    url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws/prices',
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'price_update') {
        const { symbol, price, change } = message.data;
        setPrices(prev => ({
          ...prev,
          [symbol]: {
            price,
            change,
            timestamp: message.timestamp
          }
        }));
      }
    }
  });

  // Subscribe to symbols when connected
  useEffect(() => {
    if (isConnected && symbols.length > 0) {
      subscribe(symbols);
      
      return () => {
        unsubscribe(symbols);
      };
    }
  }, [isConnected, symbols, subscribe, unsubscribe]);

  return { prices, isConnected };
}


// Hook for portfolio updates
export function usePortfolioUpdates(userId: string) {
  const [portfolio, setPortfolio] = useState<any>(null);

  const { isConnected } = useWebSocket({
    url: `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/portfolio/${userId}`,
    autoReconnect: true,
    onMessage: (message) => {
      if (message.type === 'portfolio_update') {
        setPortfolio(message.data);
      }
    }
  });

  return { portfolio, isConnected };
}
