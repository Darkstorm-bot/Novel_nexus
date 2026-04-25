import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  BookOpen,
  Play,
  Pause,
  CheckCircle,
  MessageSquare,
  Edit3,
  Eye,
  Columns,
  Loader2,
} from 'lucide-react';
import { useEditorStore, usePipelineStore, useUIStore } from '../store';
import { api } from '../api/client';
import { wsClient } from '../api/websocket';
import type { PipelineState, Chapter } from '../types';
import ChapterList from '../components/ChapterList';
import ContentEditor from '../components/ContentEditor';
import PreviewPane from '../components/PreviewPane';
import PipelineProgress from '../components/PipelineProgress';

const PHASE_ICONS: Record<string, any> = {
  concept: MessageSquare,
  outline: BookOpen,
  beat_sheet: Edit3,
  drafting: Edit3,
  critique: MessageSquare,
  rewrite: Edit3,
  polish: Edit3,
  consistency: CheckCircle,
  export: BookOpen,
};

const PHASE_COLORS: Record<string, string> = {
  concept: 'from-blue-500 to-cyan-500',
  outline: 'from-purple-500 to-pink-500',
  beat_sheet: 'from-orange-500 to-red-500',
  drafting: 'from-green-500 to-emerald-500',
  critique: 'from-yellow-500 to-orange-500',
  rewrite: 'from-indigo-500 to-purple-500',
  polish: 'from-pink-500 to-rose-500',
  consistency: 'from-teal-500 to-cyan-500',
  export: 'from-violet-500 to-purple-500',
};

const StoryEditor: React.FC = () => {
  const { storyId } = useParams<{ storyId: string }>();
  const { activeChapter, chapters, setChapters, setActiveChapter, viewMode, setViewMode } = useEditorStore();
  const { pipeline, setPipeline, isRunning, currentPhase } = usePipelineStore();
  const { addNotification } = useUIStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isStartingPipeline, setIsStartingPipeline] = useState(false);

  useEffect(() => {
    if (!storyId) return;

    // Connect WebSocket
    wsClient.connect(storyId);

    // Listen for pipeline updates
    const unsubscribe = wsClient.on('pipeline_update', (data: PipelineState) => {
      setPipeline(data);
      if (data.progress.current_step) {
        addNotification(`Pipeline: ${data.progress.current_step}`, 'info');
      }
    });

    // Load initial data
    loadStoryData();

    return () => {
      unsubscribe();
      wsClient.disconnect();
    };
  }, [storyId]);

  const loadStoryData = async () => {
    if (!storyId) return;
    setIsLoading(true);
    try {
      const [chaptersData, pipelineData] = await Promise.all([
        api.getChapters(storyId),
        api.getPipeline(storyId).catch(() => null),
      ]);
      setChapters(chaptersData);
      if (pipelineData) {
        setPipeline(pipelineData);
      }
    } catch (error) {
      addNotification('Failed to load story data', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartPipeline = async () => {
    if (!storyId) return;
    setIsStartingPipeline(true);
    try {
      const pipelineData = await api.startPipeline(storyId);
      setPipeline(pipelineData);
      addNotification('Pipeline started successfully!', 'success');
    } catch (error) {
      addNotification('Failed to start pipeline', 'error');
    } finally {
      setIsStartingPipeline(false);
    }
  };

  const handlePausePipeline = async () => {
    if (!storyId) return;
    try {
      const pipelineData = await api.pausePipeline(storyId);
      setPipeline(pipelineData);
      addNotification('Pipeline paused', 'info');
    } catch (error) {
      addNotification('Failed to pause pipeline', 'error');
    }
  };

  const handleResumePipeline = async () => {
    if (!storyId) return;
    try {
      const pipelineData = await api.resumePipeline(storyId);
      setPipeline(pipelineData);
      addNotification('Pipeline resumed', 'success');
    } catch (error) {
      addNotification('Failed to resume pipeline', 'error');
    }
  };

  const handleApprovePhase = (phase: string) => {
    if (!storyId) return;
    wsClient.approvePhase(phase);
    addNotification(`Approved ${phase} phase`, 'success');
  };

  const handleRejectPhase = (phase: string, reason: string) => {
    if (!storyId) return;
    wsClient.rejectPhase(phase, reason);
    addNotification(`Rejected ${phase} phase`, 'warning');
  };

  const handleSelectChapter = (chapter: Chapter) => {
    setActiveChapter(chapter);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Header */}
      <div className="glass p-4 rounded-xl border border-dark-700/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <BookOpen className="w-8 h-8 text-primary-400" />
            <div>
              <h1 className="text-2xl font-bold gradient-text">Story Studio</h1>
              <p className="text-sm text-dark-400">Manage your story and AI pipeline</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {!isRunning ? (
              <button
                onClick={handleStartPipeline}
                disabled={isStartingPipeline}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg font-medium hover:opacity-90 transition-all glow-primary disabled:opacity-50"
              >
                {isStartingPipeline ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                Start Pipeline
              </button>
            ) : (
              <button
                onClick={handlePausePipeline}
                className="flex items-center gap-2 px-6 py-2 bg-accent-500/20 text-accent-400 border border-accent-500/30 rounded-lg font-medium hover:bg-accent-500/30 transition-all"
              >
                <Pause className="w-5 h-5" />
                Pause
              </button>
            )}
            <div className="flex items-center gap-2 bg-dark-800/50 rounded-lg p-1">
              <button
                onClick={() => setViewMode('edit')}
                className={`p-2 rounded ${viewMode === 'edit' ? 'bg-primary-500/20 text-primary-400' : 'text-dark-400 hover:text-dark-200'}`}
              >
                <Edit3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('split')}
                className={`p-2 rounded ${viewMode === 'split' ? 'bg-primary-500/20 text-primary-400' : 'text-dark-400 hover:text-dark-200'}`}
              >
                <Columns className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('preview')}
                className={`p-2 rounded ${viewMode === 'preview' ? 'bg-primary-500/20 text-primary-400' : 'text-dark-400 hover:text-dark-200'}`}
              >
                <Eye className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Pipeline Status Bar */}
        {pipeline && (
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <PipelineProgress pipeline={pipeline} />
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className={`px-3 py-1 rounded-full ${
                pipeline.status === 'running' ? 'bg-green-500/20 text-green-400' :
                pipeline.status === 'waiting_approval' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-dark-500/20 text-dark-400'
              }`}>
                {pipeline.status.replace('_', ' ').toUpperCase()}
              </span>
              {currentPhase && (
                <span className="text-dark-400">
                  Phase: <span className="text-primary-400 font-medium">{currentPhase}</span>
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-12 gap-4 overflow-hidden">
        {/* Chapter List */}
        <div className={`${viewMode === 'preview' ? 'hidden' : 'col-span-3'} overflow-hidden`}>
          <ChapterList
            chapters={chapters}
            activeChapter={activeChapter}
            onSelectChapter={handleSelectChapter}
            storyId={storyId!}
          />
        </div>

        {/* Editor/Preview */}
        <div className={`${viewMode === 'preview' ? 'col-span-12' : viewMode === 'split' ? 'col-span-5' : 'col-span-9'} overflow-hidden`}>
          <ContentEditor
            chapter={activeChapter}
            onSave={(content) => {
              // Handle save
              addNotification('Content saved', 'success');
            }}
          />
        </div>

        {/* Preview Pane - Only show in split or preview mode */}
        {(viewMode === 'split' || viewMode === 'preview') && (
          <div className={`${viewMode === 'split' ? 'col-span-4' : 'col-span-12'} overflow-hidden`}>
            <PreviewPane chapter={activeChapter} />
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryEditor;
