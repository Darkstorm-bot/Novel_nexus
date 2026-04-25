import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Search, Database, Layers, Clock, Filter } from 'lucide-react';
import type { MemoryItem } from '../types';

const MemoryBrowser: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [memoryType, setMemoryType] = useState<string>('all');
  const [selectedMemory, setSelectedMemory] = useState<MemoryItem | null>(null);

  // Demo data - in real implementation, this would come from API
  const demoMemories: MemoryItem[] = [
    {
      id: '1',
      content: 'The protagonist discovers a hidden portal in the ancient library.',
      metadata: { type: 'plot', chapter: '3' },
      created_at: new Date().toISOString(),
    },
    {
      id: '2',
      content: 'Main character has a scar on their left hand from a childhood accident.',
      metadata: { type: 'character', character: 'John', importance: 0.7 },
      created_at: new Date().toISOString(),
    },
    {
      id: '3',
      content: 'The magical kingdom of Eldoria floats among the clouds, accessible only by flying creatures.',
      metadata: { type: 'world_building', location: 'Eldoria', importance: 0.95 },
      created_at: new Date().toISOString(),
    },
  ];

  const filteredMemories = demoMemories.filter((memory) => {
    const matchesSearch = memory.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType =
      memoryType === 'all' || memory.metadata.type === memoryType;
    return matchesSearch && matchesType;
  });

  const TYPE_COLORS: Record<string, string> = {
    plot: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    character: 'bg-green-500/20 text-green-400 border-green-500/30',
    world_building: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BrainCircuit className="w-8 h-8 text-primary-400" />
          <div>
            <h1 className="text-2xl font-bold gradient-text">Memory Browser</h1>
            <p className="text-sm text-dark-400">
              Explore the AI's story memory and consistency tracking
            </p>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-dark-700/50">
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-5 h-5 text-primary-400" />
            <span className="text-sm text-dark-400">Total Memories</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{demoMemories.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-dark-700/50">
          <div className="flex items-center gap-3 mb-2">
            <Layers className="w-5 h-5 text-accent-400" />
            <span className="text-sm text-dark-400">Vector Entries</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">{demoMemories.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-dark-700/50">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-green-400" />
            <span className="text-sm text-dark-400">Recent Updates</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">3</p>
        </div>
        <div className="glass p-4 rounded-xl border border-dark-700/50">
          <div className="flex items-center gap-3 mb-2">
            <BrainCircuit className="w-5 h-5 text-purple-400" />
            <span className="text-sm text-dark-400">Avg. Importance</span>
          </div>
          <p className="text-2xl font-bold text-dark-100">0.85</p>
        </div>
      </div>

      {/* Filters */}
      <div className="glass p-4 rounded-xl border border-dark-700/50 flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="w-5 h-5 text-dark-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search memories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-dark-500" />
          <select
            value={memoryType}
            onChange={(e) => setMemoryType(e.target.value)}
            className="px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
          >
            <option value="all">All Types</option>
            <option value="plot">Plot</option>
            <option value="character">Character</option>
            <option value="world_building">World Building</option>
          </select>
        </div>
      </div>

      {/* Memory List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Memories */}
        <div className="glass rounded-xl border border-dark-700/50 overflow-hidden">
          <div className="p-4 border-b border-dark-700/50">
            <h3 className="font-semibold text-dark-100">Memory Entries</h3>
          </div>
          <div className="max-h-[600px] overflow-y-auto divide-y divide-dark-700/50">
            {filteredMemories.map((memory) => (
              <motion.div
                key={memory.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={() => setSelectedMemory(memory)}
                className={`p-4 cursor-pointer hover:bg-dark-800/50 transition-colors ${
                  selectedMemory?.id === memory.id ? 'bg-primary-500/10' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span
                    className={`text-xs px-2 py-1 rounded-full border ${
                      TYPE_COLORS[memory.metadata.type] || 'bg-dark-500/20 text-dark-400'
                    }`}
                  >
                    {memory.metadata.type}
                  </span>
                  <span className="text-xs text-dark-500">
                    Score: {((memory.metadata.importance || 0) * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-sm text-dark-300 line-clamp-2">{memory.content}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-dark-500">
                  <span>ID: {memory.id}</span>
                  <span>{new Date(memory.created_at).toLocaleDateString()}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Memory Details */}
        <div className="glass rounded-xl border border-dark-700/50 overflow-hidden">
          <div className="p-4 border-b border-dark-700/50">
            <h3 className="font-semibold text-dark-100">Memory Details</h3>
          </div>
          <div className="p-6">
            {selectedMemory ? (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-dark-400 mb-2">Content</h4>
                  <p className="text-dark-100">{selectedMemory.content}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-dark-400 mb-2">Metadata</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedMemory.metadata).map(([key, value]) => (
                      <div
                        key={key}
                        className="p-2 bg-dark-800/50 rounded-lg border border-dark-700/50"
                      >
                        <span className="text-xs text-dark-500 capitalize">{key}</span>
                        <p className="text-sm text-dark-100">{String(value)}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-dark-400 mb-2">Embedding Info</h4>
                  <div className="p-3 bg-dark-800/50 rounded-lg border border-dark-700/50">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-dark-400">Vector Dimensions</span>
                      <span className="text-dark-100">384</span>
                    </div>
                    <div className="flex items-center justify-between text-sm mt-2">
                      <span className="text-dark-400">Model</span>
                      <span className="text-dark-100">sentence-transformers</span>
                    </div>
                  </div>
                </div>
                <div className="pt-4 border-t border-dark-700/50">
                  <button className="w-full px-4 py-2 bg-primary-500/20 text-primary-400 border border-primary-500/30 rounded-lg hover:bg-primary-500/30 transition-all">
                    View Vector Data
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <BrainCircuit className="w-16 h-16 text-dark-600 mx-auto mb-4" />
                <p className="text-dark-400">Select a memory to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Vector Visualization Placeholder */}
      <div className="glass p-6 rounded-xl border border-dark-700/50">
        <h3 className="font-semibold text-dark-100 mb-4">Vector Space Visualization</h3>
        <div className="h-64 bg-dark-900/50 rounded-lg border border-dark-700/50 flex items-center justify-center">
          <div className="text-center">
            <Layers className="w-12 h-12 text-dark-600 mx-auto mb-3" />
            <p className="text-dark-400">
              Interactive vector space visualization would appear here
            </p>
            <p className="text-sm text-dark-500 mt-1">
              Showing semantic relationships between story elements
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryBrowser;
