import React from 'react';
import { BookOpen, FileText } from 'lucide-react';
import type { Chapter } from '../types';

interface PreviewPaneProps {
  chapter: Chapter | null;
}

const PreviewPane: React.FC<PreviewPaneProps> = ({ chapter }) => {
  if (!chapter) {
    return (
      <div className="h-full glass rounded-xl border border-dark-700/50 flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400">Select a chapter to preview</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full glass rounded-xl border border-dark-700/50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-primary-400" />
          <h2 className="font-semibold text-dark-100">Preview</h2>
        </div>
        <span className="text-xs text-dark-500">{chapter.word_count} words</span>
      </div>

      {/* Preview Content */}
      <div className="flex-1 overflow-y-auto p-6 bg-dark-900/30">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold text-dark-100 mb-2">{chapter.title}</h1>
          {chapter.summary && (
            <div className="mb-6 p-4 bg-dark-800/50 rounded-lg border border-dark-700/50">
              <h3 className="text-sm font-medium text-dark-300 mb-2">Summary</h3>
              <p className="text-sm text-dark-400">{chapter.summary}</p>
            </div>
          )}
          <div className="prose prose-invert max-w-none font-serif leading-relaxed">
            {chapter.content ? (
              <div dangerouslySetInnerHTML={{ __html: chapter.content.replace(/\n/g, '<br/>') }} />
            ) : (
              <p className="text-dark-500 italic">No content available for preview.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreviewPane;
