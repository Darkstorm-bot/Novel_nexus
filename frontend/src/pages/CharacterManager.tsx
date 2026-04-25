import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Plus, Edit2, Trash2, Search, Filter } from 'lucide-react';
import { useEditorStore, useUIStore } from '../store';
import type { Character, CharacterCreate } from '../types';

const CharacterManager: React.FC = () => {
  const { characters, setCharacters, selectedCharacter, setSelectedCharacter } = useEditorStore();
  const { addNotification } = useUIStore();
  const [showNewCharacterModal, setShowNewCharacterModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [newCharacter, setNewCharacter] = useState<CharacterCreate>({
    story_id: 'temp',
    name: '',
    role: 'supporting',
    traits: [],
    motivations: [],
  });

  const filteredCharacters = characters.filter((char) => {
    const matchesSearch = char.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || char.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const handleCreateCharacter = () => {
    // In real implementation, this would call API
    addNotification('Character created (demo)', 'success');
    setShowNewCharacterModal(false);
  };

  const ROLE_COLORS: Record<string, string> = {
    protagonist: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    antagonist: 'bg-red-500/20 text-red-400 border-red-500/30',
    supporting: 'bg-green-500/20 text-green-400 border-green-500/30',
    minor: 'bg-dark-500/20 text-dark-400 border-dark-500/30',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-primary-400" />
          <div>
            <h1 className="text-2xl font-bold gradient-text">Characters</h1>
            <p className="text-sm text-dark-400">Manage your story's cast</p>
          </div>
        </div>
        <button
          onClick={() => setShowNewCharacterModal(true)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg font-medium hover:opacity-90 transition-all glow-primary"
        >
          <Plus className="w-5 h-5" />
          New Character
        </button>
      </div>

      {/* Filters */}
      <div className="glass p-4 rounded-xl border border-dark-700/50 flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="w-5 h-5 text-dark-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search characters..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-dark-500" />
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
          >
            <option value="all">All Roles</option>
            <option value="protagonist">Protagonist</option>
            <option value="antagonist">Antagonist</option>
            <option value="supporting">Supporting</option>
            <option value="minor">Minor</option>
          </select>
        </div>
      </div>

      {/* Characters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCharacters.map((character) => (
          <motion.div
            key={character.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            className="glass p-6 rounded-xl border border-dark-700/50 cursor-pointer hover:border-primary-500/30 transition-all"
            onClick={() => setSelectedCharacter(character)}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-dark-100">{character.name}</h3>
                <span
                  className={`text-xs px-2 py-1 rounded-full border ${
                    ROLE_COLORS[character.role]
                  }`}
                >
                  {character.role}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 hover:bg-dark-800/50 rounded-lg transition-colors text-dark-400 hover:text-primary-400">
                  <Edit2 className="w-4 h-4" />
                </button>
                <button className="p-2 hover:bg-dark-800/50 rounded-lg transition-colors text-dark-400 hover:text-red-400">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {character.description && (
              <p className="text-sm text-dark-400 mb-4 line-clamp-2">
                {character.description}
              </p>
            )}

            {character.traits?.length > 0 && (
              <div className="mb-3">
                <h4 className="text-xs font-medium text-dark-500 mb-2">Traits</h4>
                <div className="flex flex-wrap gap-2">
                  {character.traits.slice(0, 3).map((trait, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 bg-dark-800/50 rounded text-dark-300"
                    >
                      {trait}
                    </span>
                  ))}
                  {character.traits.length > 3 && (
                    <span className="text-xs text-dark-500">
                      +{character.traits.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-dark-500">
              <span>{character.appearance_count} appearances</span>
              <span>Last seen: Ch. {character.state?.last_seen_chapter || '-'}</span>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredCharacters.length === 0 && (
        <div className="glass p-12 rounded-xl border border-dark-700/50 text-center">
          <Users className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-dark-300 mb-2">No characters found</h3>
          <p className="text-dark-400">
            {characters.length === 0
              ? 'Create your first character to get started'
              : 'Try adjusting your search or filters'}
          </p>
        </div>
      )}

      {/* New Character Modal */}
      {showNewCharacterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass p-8 rounded-2xl border border-dark-700/50 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          >
            <h2 className="text-2xl font-bold gradient-text mb-6">Create New Character</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleCreateCharacter();
              }}
              className="space-y-4"
            >
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Name *
                  </label>
                  <input
                    type="text"
                    value={newCharacter.name}
                    onChange={(e) =>
                      setNewCharacter({ ...newCharacter, name: e.target.value })
                    }
                    className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Role *
                  </label>
                  <select
                    value={newCharacter.role}
                    onChange={(e) =>
                      setNewCharacter({
                        ...newCharacter,
                        role: e.target.value as any,
                      })
                    }
                    className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
                  >
                    <option value="protagonist">Protagonist</option>
                    <option value="antagonist">Antagonist</option>
                    <option value="supporting">Supporting</option>
                    <option value="minor">Minor</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Description
                </label>
                <textarea
                  value={newCharacter.description || ''}
                  onChange={(e) =>
                    setNewCharacter({ ...newCharacter, description: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100 resize-none"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">
                  Background
                </label>
                <textarea
                  value={newCharacter.background || ''}
                  onChange={(e) =>
                    setNewCharacter({ ...newCharacter, background: e.target.value })
                  }
                  className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100 resize-none"
                  rows={4}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewCharacterModal(false)}
                  className="flex-1 px-4 py-2 bg-dark-800/50 text-dark-300 rounded-lg hover:bg-dark-700/50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-primary-500 to-accent-500 text-white rounded-lg hover:opacity-90 transition-opacity"
                >
                  Create Character
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default CharacterManager;
