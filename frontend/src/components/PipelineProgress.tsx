import React from 'react';
import { motion } from 'framer-motion';
import type { PipelineState, PipelinePhase } from '../types';

interface PipelineProgressProps {
  pipeline: PipelineState;
}

const PHASE_NAMES: Record<PipelinePhase, string> = {
  concept: 'Concept',
  outline: 'Outline',
  beat_sheet: 'Beat Sheet',
  drafting: 'Drafting',
  critique: 'Critique',
  rewrite: 'Rewrite',
  polish: 'Polish',
  consistency: 'Consistency',
  export: 'Export',
};

const PHASE_COLORS: Record<PipelinePhase, string> = {
  concept: 'bg-blue-500',
  outline: 'bg-purple-500',
  beat_sheet: 'bg-orange-500',
  drafting: 'bg-green-500',
  critique: 'bg-yellow-500',
  rewrite: 'bg-indigo-500',
  polish: 'bg-pink-500',
  consistency: 'bg-teal-500',
  export: 'bg-violet-500',
};

const PipelineProgress: React.FC<PipelineProgressProps> = ({ pipeline }) => {
  const phases: PipelinePhase[] = [
    'concept',
    'outline',
    'beat_sheet',
    'drafting',
    'critique',
    'rewrite',
    'polish',
    'consistency',
    'export',
  ];

  const currentPhaseIndex = pipeline.current_phase
    ? phases.indexOf(pipeline.current_phase)
    : -1;

  return (
    <div className="w-full">
      {/* Progress Bar */}
      <div className="flex items-center gap-1 mb-3">
        {phases.map((phase, index) => {
          const isCompleted = index < currentPhaseIndex;
          const isCurrent = index === currentPhaseIndex;
          const isPending = index > currentPhaseIndex;

          return (
            <div key={phase} className="flex-1 flex items-center">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                className={`h-2 rounded-full flex-1 transition-all ${
                  isCompleted
                    ? PHASE_COLORS[phase]
                    : isCurrent
                    ? `${PHASE_COLORS[phase]} animate-pulse`
                    : 'bg-dark-700'
                }`}
              />
              {index < phases.length - 1 && (
                <div
                  className={`w-8 h-0.5 ${
                    isCompleted ? 'bg-dark-600' : 'bg-dark-800'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Phase Labels */}
      <div className="flex justify-between text-xs">
        {phases.map((phase, index) => {
          const isCompleted = index < currentPhaseIndex;
          const isCurrent = index === currentPhaseIndex;

          return (
            <div
              key={phase}
              className={`flex-1 text-center ${
                isCurrent ? 'text-primary-400 font-medium' : 'text-dark-500'
              }`}
            >
              <div
                className={`w-6 h-6 mx-auto mb-1 rounded-full flex items-center justify-center ${
                  isCompleted
                    ? PHASE_COLORS[phase]
                    : isCurrent
                    ? 'border-2 border-primary-400 bg-dark-800'
                    : 'border border-dark-600 bg-dark-800'
                }`}
              >
                {isCompleted && (
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                )}
                {isCurrent && <div className="w-2 h-2 rounded-full bg-primary-400" />}
              </div>
              <span className="hidden lg:inline">{PHASE_NAMES[phase]}</span>
            </div>
          );
        })}
      </div>

      {/* Progress Percentage */}
      <div className="mt-3 text-center">
        <span className="text-sm text-dark-400">
          Overall Progress:{' '}
          <span className="text-primary-400 font-semibold">
            {pipeline.progress.progress_percentage.toFixed(0)}%
          </span>
        </span>
      </div>
    </div>
  );
};

export default PipelineProgress;
