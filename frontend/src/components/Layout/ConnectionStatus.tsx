import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

interface ConnectionStatusProps {
  connected: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ connected }) => {
  return (
    <div className="flex items-center space-x-2 text-sm">
      {connected ? (
        <>
          <Wifi className="w-4 h-4 text-green-400" />
          <span className="text-green-400">Connected</span>
        </>
      ) : (
        <>
          <WifiOff className="w-4 h-4 text-red-400" />
          <span className="text-red-400">Disconnected</span>
        </>
      )}
    </div>
  );
};
