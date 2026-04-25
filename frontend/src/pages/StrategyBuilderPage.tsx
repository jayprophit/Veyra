import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { api } from '../services/api';
import { 
  Plus, Save, Play, Download, Share2, 
  GitBranch, Settings, ChevronRight 
} from 'lucide-react';
import toast from 'react-hot-toast';

interface StrategyNode {
  id: string;
  type: string;
  subtype: string;
  params: Record<string, any>;
  position: { x: number; y: number };
}

export default function StrategyBuilderPage() {
  const [strategyName, setStrategyName] = useState('');
  const [description, setDescription] = useState('');
  const [nodes, setNodes] = useState<StrategyNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const createStrategy = useMutation(
    (data: { name: string; description: string }) =>
      api.post('/api/v2/strategy/visual/create', data),
    {
      onSuccess: () => {
        toast.success('Strategy created successfully!');
      },
      onError: () => {
        toast.error('Failed to create strategy');
      }
    }
  );

  const addNode = (type: string, subtype: string) => {
    const newNode: StrategyNode = {
      id: `node-${Date.now()}`,
      type,
      subtype,
      params: {},
      position: { x: 100 + nodes.length * 50, y: 100 }
    };
    setNodes([...nodes, newNode]);
    toast.success(`Added ${subtype} node`);
  };

  const handleCreate = () => {
    if (!strategyName) {
      toast.error('Please enter a strategy name');
      return;
    }
    createStrategy.mutate({ name: strategyName, description });
  };

  const nodeTypes = [
    { type: 'indicator', label: 'SMA', icon: '📊' },
    { type: 'indicator', label: 'RSI', icon: '📈' },
    { type: 'indicator', label: 'MACD', icon: '📉' },
    { type: 'condition', label: 'Crossover', icon: '↔️' },
    { type: 'condition', label: 'Threshold', icon: '⚡' },
    { type: 'action', label: 'Buy', icon: '🟢' },
    { type: 'action', label: 'Sell', icon: '🔴' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Visual Strategy Builder</h1>
        <p className="text-gray-600 mt-1">Drag-and-drop algorithm construction</p>
      </div>

      {/* Strategy Info */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Strategy Name
            </label>
            <input
              type="text"
              value={strategyName}
              onChange={(e) => setStrategyName(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="My Custom Strategy"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Strategy description..."
            />
          </div>
        </div>
        <div className="mt-4 flex gap-2">
          <button
            onClick={handleCreate}
            disabled={createStrategy.isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            {createStrategy.isLoading ? 'Creating...' : 'Create Strategy'}
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            <Save className="w-4 h-4" />
            Save Draft
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            <Download className="w-4 h-4" />
            Export Code
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Node Palette */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Node Palette</h3>
          <div className="space-y-2">
            {nodeTypes.map((node) => (
              <button
                key={node.label}
                onClick={() => addNode(node.type, node.label.toLowerCase())}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all"
              >
                <span className="text-xl">{node.icon}</span>
                <div className="text-left">
                  <div className="font-medium text-sm">{node.label}</div>
                  <div className="text-xs text-gray-500 capitalize">{node.type}</div>
                </div>
                <Plus className="w-4 h-4 ml-auto text-gray-400" />
              </button>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t">
            <h4 className="font-medium text-gray-900 mb-2">Templates</h4>
            <button className="w-full text-left p-2 rounded hover:bg-gray-50 text-sm">
              📈 MA Crossover
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-gray-50 text-sm">
              ⚡ RSI Oversold
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-gray-50 text-sm">
              📊 MACD Momentum
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div className="col-span-2 bg-gray-50 rounded-lg shadow min-h-[500px] relative overflow-hidden">
          <div className="absolute inset-0 bg-grid-pattern opacity-5" />
          
          {nodes.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                <GitBranch className="w-16 h-16 mx-auto mb-4" />
                <p>Click nodes from the palette to start building</p>
              </div>
            </div>
          ) : (
            <div className="p-4">
              {nodes.map((node, index) => (
                <div
                  key={node.id}
                  className={`absolute bg-white rounded-lg shadow-md p-4 cursor-pointer transition-all hover:shadow-lg ${
                    selectedNode === node.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                  style={{
                    left: node.position.x,
                    top: node.position.y,
                    width: '180px'
                  }}
                  onClick={() => setSelectedNode(node.id)}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">
                      {node.type === 'indicator' ? '📊' : 
                       node.type === 'condition' ? '⚡' : 
                       node.type === 'action' ? (node.subtype === 'buy' ? '🟢' : '🔴') : '⚙️'}
                    </span>
                    <span className="font-medium capitalize">{node.subtype}</span>
                  </div>
                  <div className="text-xs text-gray-500 capitalize">{node.type}</div>
                  {index < nodes.length - 1 && (
                    <div className="absolute -right-6 top-1/2 transform -translate-y-1/2">
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Properties Panel */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-semibold text-gray-900 mb-4">Properties</h3>
          {selectedNode ? (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Node ID
                </label>
                <div className="text-sm text-gray-600 font-mono">{selectedNode}</div>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Parameters
                </label>
                <div className="space-y-2">
                  <div>
                    <label className="text-xs text-gray-500">Period</label>
                    <input
                      type="number"
                      defaultValue={20}
                      className="w-full px-2 py-1 text-sm border rounded"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Source</label>
                    <select className="w-full px-2 py-1 text-sm border rounded">
                      <option>Close</option>
                      <option>Open</option>
                      <option>High</option>
                      <option>Low</option>
                    </select>
                  </div>
                </div>
              </div>
              <button className="w-full px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 text-sm">
                Delete Node
              </button>
            </div>
          ) : (
            <div className="text-gray-400 text-center py-8">
              <Settings className="w-8 h-8 mx-auto mb-2" />
              <p className="text-sm">Select a node to edit properties</p>
            </div>
          )}

          <div className="mt-6 pt-6 border-t">
            <h4 className="font-medium text-gray-900 mb-2">Actions</h4>
            <button className="w-full flex items-center gap-2 p-2 rounded hover:bg-gray-50 text-sm">
              <Play className="w-4 h-4" />
              Backtest Strategy
            </button>
            <button className="w-full flex items-center gap-2 p-2 rounded hover:bg-gray-50 text-sm">
              <Share2 className="w-4 h-4" />
              Publish to Marketplace
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
