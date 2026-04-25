import { useEffect, useRef, useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

interface WSMessage {
  stream: string;
  type: string;
  data: any;
  timestamp: string;
}

export const useWebSocket = () => {
  const [connected, setConnected] = useState(false);
  const [prices, setPrices] = useState<Record<string, any>>({});
  const [orders, setOrders] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/v1/market');
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');

      // Subscribe to streams
      ws.send(JSON.stringify({
        action: 'subscribe',
        streams: ['prices', 'orders', 'alerts']
      }));
    };

    ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);

        switch (message.stream) {
          case 'prices':
            setPrices((prev) => ({
              ...prev,
              [message.data.symbol]: message.data
            }));
            break;

          case 'orders':
            setOrders((prev) => [...prev, message.data]);
            if (message.data.status === 'filled') {
              toast.success(`Order ${message.data.order_id} filled!`);
            }
            break;

          case 'alerts':
            setAlerts((prev) => [...prev.slice(-9), message.data]);
            if (message.data.severity === 'high') {
              toast.error(message.data.message);
            }
            break;
        }
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
      
      // Reconnect after 5 seconds
      setTimeout(() => {
        connect();
      }, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return {
    connected,
    prices,
    orders,
    alerts,
    sendMessage
  };
};
