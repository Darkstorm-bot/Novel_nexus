import React from 'react';
import { Activity, Play, Pause, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { usePipelineStore, useUIStore } from '../store';
import type { PipelinePhase } from '../types';

const PHASE_NAMES: Record<PipelinePhase, string> = {
  concept: 'Concept Development',
  outline: 'Outline Generation',
  beat_sheet: 'Beat Sheet Creation',
  drafting: 'Draft Writing',
  critique: 'Critique & Analysis',
  rewrite: 'Rewriting',
  polish: 'Polishing',
  consistency: 'Consistency Check',
  export: 'Export',
};

const PHASE_ICONS: Record<PipelinePhase, any> = {
  concept: Activity,
  outline: Activity,
  beat_sheet: Activity,
  drafting: Activity,
  critique: AlertCircle,
  rewrite: Activity,
  polish: Activity,
  consistency: CheckCircle,
  export: CheckCircle,
};

const PipelineMonitor: React.FC = () => {
  const { pipeline, isRunning, currentPhase } = usePipelineStore();
  const { addNotification } = useUIStore();

  const handleStart = async () => {
    // This would need a storyId in real implementation
    addNotification('Please select a story first', 'warning');
  };

  const handlePause = async () => {
    addNotification('Pause functionality requires story context', 'info');
  };

  if (!pipeline) {
    return (
      <div className="space-y-6">
        <div className="glass p-8 rounded-xl border border-dark-700/50 text-center">
          <Activity className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-dark-100 mb-2">No Active Pipeline</h2>
          <p className="text-dark-400 mb-6">
            Start the AI writing pipeline to generate your story
          </p>
          <button
            onClick={handleStart}
            className="px-6 py-3 bg-gradient-to-r from-primary-500 to-accent-500 text-white rounded-lg font-medium hover:opacity-90 transition-all glow-primary"
          >
            Start New Pipeline
          </button>
        </div>

        {/* Pipeline Phases Overview */}
        <div className="glass p-6 rounded-xl border border-dark-700/50">
          <h3 className="text-lg font-semibold text-dark-100 mb-4">Pipeline Phases</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(PHASE_NAMES).map(([phase, name], index) => {
              const Icon = PHASE_ICONS[phase as PipelinePhase];
              return (
                <div
                  key={phase}
                  className="p-4 bg-dark-800/50 rounded-lg border border-dark-700/50"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-xs text-dark-500 font-mono">
                      Phase {index + 1}
                    </span>
                    <Icon className="w-4 h-4 text-primary-400" />
                  </div>
                  <h4 className="font-medium text-dark-100">{name}</h4>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="glass p-6 rounded-xl border border-dark-700/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div
              className={`w-3 h-3 rounded-full ${
                isRunning
                  ? 'bg-green-500 animate-pulse'
                  : pipeline.status === 'waiting_approval'
                  ? 'bg-yellow-500'
                  : 'bg-dark-500'
              }`}
            />
            <h2 className="text-xl font-bold text-dark-100">Pipeline Status</h2>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`px-3 py-1 rounded-full text-sm ${
                pipeline.status === 'running'
                  ? 'bg-green-500/20 text-green-400'
                  : pipeline.status === 'waiting_approval'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-dark-500/20 text-dark-400'
              }`}
            >
              {pipeline.status.replace('_', ' ').toUpperCase()}
            </span>
            {isRunning ? (
              <button
                onClick={handlePause}
                className="flex items-center gap-2 px-4 py-2 bg-accent-500/20 text-accent-400 border border-accent-500/30 rounded-lg hover:bg-accent-500/30 transition-all"
              >
                <Pause className="w-4 h-4" />
                Pause
              </button>
            ) : (
              <button
                onClick={handleStart}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500/20 text-primary-400 border border-primary-500/30 rounded-lg hover:bg-primary-500/30 transition-all"
              >
                <Play className="w-4 h-4" />
                Resume
              </button>
            )}
          </div>
        </div>

        {/* Current Phase */}
        {currentPhase && (
          <div className="p-4 bg-dark-800/50 rounded-lg border border-dark-700/50">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-5 h-5 text-primary-400" />
              <span className="text-sm text-dark-400">Current Phase</span>
            </div>
            <h3 className="text-lg font-semibold text-dark-100">
              {PHASE_NAMES[currentPhase as PipelinePhase]}
            </h3>
            <div className="mt-3">
              <div className="w-full bg-dark-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full transition-all"
                  style={{ width: `${pipeline.progress.progress_percentage}%` }}
                />
              </div>
              <p className="text-sm text-dark-400 mt-2">
                {pipeline.progress.progress_percentage.toFixed(0)}% complete
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Phase Results */}
      <div className="glass p-6 rounded-xl border border-dark-700/50">
        <h3 className="text-lg font-semibold text-dark-100 mb-4">Phase History</h3>
        <div className="space-y-3">
          {Object.entries(pipeline.progress.phase_results || {}).map(
            ([phase, result]) => {
              const Icon =
                result.status === 'success'
                  ? CheckCircle
                  : result.status === 'failed'
                  ? AlertCircle
                  : Clock;
              return (
                <div
                  key={phase}
                  className="flex items-center justify-between p-4 bg-dark-800/50 rounded-lg border border-dark-700/50"
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-5 h-5 ${
                        result.status === 'success'
                          ? 'text-green-400'
                          : result.status === 'failed'
                          ? 'text-red-400'
                          : 'text-yellow-400'
                      }`}
                    />
                    <div>
                      <h4 className="font-medium text-dark-100">
                        {PHASE_NAMES[phase as PipelinePhase]}
                      </h4>
                      {result.errors?.length > 0 && (
                        <p className="text-sm text-red-400">{result.errors[0]}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        result.status === 'success'
                          ? 'bg-green-500/20 text-green-400'
                          : result.status === 'failed'
                          ? 'bg-red-500/20 text-red-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}
                    >
                      {result.status}
                    </span>
                    {result.completed_at && (
                      <p className="text-xs text-dark-500 mt-1">
                        {new Date(result.completed_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              );
            }
          )}
          {Object.keys(pipeline.progress.phase_results || {}).length === 0 && (
            <p className="text-dark-400 text-center py-8">
              No phases completed yet
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PipelineMonitor;
