import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, BookOpen, Clock, TrendingUp, Sparkles, Zap, BrainCircuit } from 'lucide-react';
import { useStoryStore, useUIStore } from '../store';
import { api } from '../api/client';
import type { StoryCreate } from '../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { stories, setLoading, addStory } = useStoryStore();
  const { addNotification } = useUIStore();
  const [showNewStoryModal, setShowNewStoryModal] = useState(false);
  const [newStory, setNewStory] = useState<StoryCreate>({ title: '', tags: [] });

  const stats = [
    { icon: BookOpen, label: 'Total Stories', value: stories.length.toString(), color: 'from-primary-500 to-primary-600' },
    { icon: Clock, label: 'In Progress', value: stories.filter(s => s.status === 'in_progress').length.toString(), color: 'from-accent-500 to-accent-600' },
    { icon: TrendingUp, label: 'Completed', value: stories.filter(s => s.status === 'completed').length.toString(), color: 'from-green-500 to-green-600' },
    { icon: BrainCircuit, label: 'Active Pipelines', value: '0', color: 'from-purple-500 to-purple-600' },
  ];

  const features = [
    { icon: Sparkles, title: 'AI Writing', description: 'Generate content with advanced LLMs', path: '/pipeline' },
    { icon: Zap, title: 'Fast Pipeline', description: '9-phase automated story generation', path: '/pipeline' },
    { icon: BrainCircuit, title: 'Memory System', description: 'Vector-based story consistency', path: '/memory' },
  ];

  const handleCreateStory = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const story = await api.createStory(newStory);
      addStory(story);
      addNotification('Story created successfully!', 'success');
      setShowNewStoryModal(false);
      navigate(`/story/${story.id}`);
    } catch (error) {
      addNotification('Failed to create story', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Welcome to Narrative Nexus</h1>
          <p className="text-dark-400">Your AI-powered collaborative story writing platform</p>
        </div>
        <button
          onClick={() => setShowNewStoryModal(true)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg font-medium hover:opacity-90 transition-all glow-primary"
        >
          <Plus className="w-5 h-5" />
          New Story
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass p-6 rounded-xl border border-dark-700/50"
            >
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center mb-4`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <p className="text-2xl font-bold text-dark-100">{stat.value}</p>
              <p className="text-sm text-dark-400">{stat.label}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Features */}
      <div>
        <h2 className="text-xl font-bold text-dark-100 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.button
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 + 0.4 }}
                onClick={() => navigate(feature.path)}
                className="glass p-6 rounded-xl border border-dark-700/50 text-left hover:border-primary-500/30 transition-all group"
              >
                <div className="w-12 h-12 rounded-lg bg-dark-800/50 flex items-center justify-center mb-4 group-hover:bg-primary-500/20 transition-colors">
                  <Icon className="w-6 h-6 text-primary-400" />
                </div>
                <h3 className="text-lg font-semibold text-dark-100 mb-2">{feature.title}</h3>
                <p className="text-sm text-dark-400">{feature.description}</p>
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Recent Stories */}
      <div>
        <h2 className="text-xl font-bold text-dark-100 mb-4">Recent Stories</h2>
        {stories.length === 0 ? (
          <div className="glass p-12 rounded-xl border border-dark-700/50 text-center">
            <BookOpen className="w-16 h-16 text-dark-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-dark-300 mb-2">No stories yet</h3>
            <p className="text-dark-400 mb-4">Create your first story to get started</p>
            <button
              onClick={() => setShowNewStoryModal(true)}
              className="px-6 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors"
            >
              Create Story
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stories.slice(0, 6).map((story) => (
              <motion.div
                key={story.id}
                whileHover={{ scale: 1.02 }}
                className="glass p-6 rounded-xl border border-dark-700/50 cursor-pointer hover:border-primary-500/30 transition-all"
                onClick={() => navigate(`/story/${story.id}`)}
              >
                <h3 className="text-lg font-semibold text-dark-100 mb-2">{story.title}</h3>
                <p className="text-sm text-dark-400 mb-4 line-clamp-2">{story.description || 'No description'}</p>
                <div className="flex items-center justify-between">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    story.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    story.status === 'in_progress' ? 'bg-accent-500/20 text-accent-400' :
                    'bg-dark-500/20 text-dark-400'
                  }`}>
                    {story.status.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-dark-500">{story.word_count} words</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* New Story Modal */}
      {showNewStoryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass p-8 rounded-2xl border border-dark-700/50 w-full max-w-md"
          >
            <h2 className="text-2xl font-bold gradient-text mb-6">Create New Story</h2>
            <form onSubmit={handleCreateStory} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">Title</label>
                <input
                  type="text"
                  value={newStory.title}
                  onChange={(e) => setNewStory({ ...newStory, title: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">Description</label>
                <textarea
                  value={newStory.description || ''}
                  onChange={(e) => setNewStory({ ...newStory, description: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100 resize-none"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-dark-300 mb-2">Genre</label>
                <input
                  type="text"
                  value={newStory.genre || ''}
                  onChange={(e) => setNewStory({ ...newStory, genre: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800/50 border border-dark-700 rounded-lg focus:outline-none focus:border-primary-500 text-dark-100"
                />
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNewStoryModal(false)}
                  className="flex-1 px-4 py-2 bg-dark-800/50 text-dark-300 rounded-lg hover:bg-dark-700/50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-primary-500 to-accent-500 text-white rounded-lg hover:opacity-90 transition-opacity"
                >
                  Create
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
