import React from 'react';
import { Edit3, Save, Bold, Italic, Underline } from 'lucide-react';
import type { Chapter } from '../types';

interface ContentEditorProps {
  chapter: Chapter | null;
  onSave: (content: string) => void;
}

const ContentEditor: React.FC<ContentEditorProps> = ({ chapter, onSave }) => {
  const [content, setContent] = React.useState(chapter?.content || '');
  const [isEditing, setIsEditing] = React.useState(false);

  React.useEffect(() => {
    setContent(chapter?.content || '');
  }, [chapter]);

  const handleSave = () => {
    onSave(content);
    setIsEditing(false);
  };

  if (!chapter) {
    return (
      <div className="h-full glass rounded-xl border border-dark-700/50 flex items-center justify-center">
        <div className="text-center">
          <Edit3 className="w-16 h-16 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-400">Select a chapter to start editing</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full glass rounded-xl border border-dark-700/50 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="font-semibold text-dark-100">{chapter.title}</h2>
          <span className="text-xs text-dark-500">{chapter.word_count} words</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-dark-800/50 rounded-lg p-1">
            <button className="p-2 hover:bg-dark-700/50 rounded transition-colors text-dark-400 hover:text-dark-200">
              <Bold className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-dark-700/50 rounded transition-colors text-dark-400 hover:text-dark-200">
              <Italic className="w-4 h-4" />
            </button>
            <button className="p-2 hover:bg-dark-700/50 rounded transition-colors text-dark-400 hover:text-dark-200">
              <Underline className="w-4 h-4" />
            </button>
          </div>
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500/20 text-primary-400 border border-primary-500/30 rounded-lg hover:bg-primary-500/30 transition-all"
              >
                <Save className="w-4 h-4" />
                Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 bg-dark-800/50 text-dark-300 rounded-lg hover:bg-dark-700/50 transition-colors"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-500 to-accent-500 text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              <Edit3 className="w-4 h-4" />
              Edit
            </button>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-y-auto p-6">
        {isEditing ? (
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full h-full bg-transparent border-none focus:outline-none text-dark-100 resize-none font-serif leading-relaxed"
            placeholder="Start writing your chapter..."
          />
        ) : (
          <div className="prose prose-invert max-w-none">
            {content || (
              <p className="text-dark-500 italic">No content yet. Click "Edit" to start writing.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentEditor;
