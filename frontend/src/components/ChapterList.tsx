import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Plus, MoreVertical } from 'lucide-react';
import type { Chapter } from '../types';

interface ChapterListProps {
  chapters: Chapter[];
  activeChapter: Chapter | null;
  onSelectChapter: (chapter: Chapter) => void;
  storyId?: string;
}

const ChapterList: React.FC<ChapterListProps> = ({
  chapters,
  activeChapter,
  onSelectChapter,
  storyId,
}) => {
  return (
    <div className="h-full glass rounded-xl border border-dark-700/50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <h2 className="font-semibold text-dark-100">Chapters</h2>
        <button className="p-2 hover:bg-dark-800/50 rounded-lg transition-colors">
          <Plus className="w-5 h-5 text-primary-400" />
        </button>
      </div>

      {/* Chapter List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {chapters.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-dark-600 mx-auto mb-3" />
            <p className="text-sm text-dark-400">No chapters yet</p>
          </div>
        ) : (
          chapters.map((chapter, index) => (
            <motion.button
              key={chapter.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onSelectChapter(chapter)}
              className={`w-full p-3 rounded-lg text-left transition-all ${
                activeChapter?.id === chapter.id
                  ? 'bg-primary-500/20 border border-primary-500/30 glow-primary'
                  : 'hover:bg-dark-800/50 border border-transparent'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-dark-500 font-mono">
                      Ch. {chapter.order + 1}
                    </span>
                    <h3 className="text-sm font-medium text-dark-100 truncate">
                      {chapter.title}
                    </h3>
                  </div>
                  {chapter.summary && (
                    <p className="text-xs text-dark-400 line-clamp-2">
                      {chapter.summary}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-xs text-dark-500">
                    <span>{chapter.word_count} words</span>
                    <span>•</span>
                    <span>{new Date(chapter.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <button className="p-1 hover:bg-dark-700/50 rounded transition-colors">
                  <MoreVertical className="w-4 h-4 text-dark-400" />
                </button>
              </div>
            </motion.button>
          ))
        )}
      </div>
    </div>
  );
};

export default ChapterList;
