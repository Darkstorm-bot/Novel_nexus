import { create } from 'zustand';
import type { Story, PipelineState, Character, Chapter } from '../types';

interface StoryStore {
  // Stories
  stories: Story[];
  currentStory: Story | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setStories: (stories: Story[]) => void;
  setCurrentStory: (story: Story | null) => void;
  addStory: (story: Story) => void;
  updateStory: (story: Story) => void;
  removeStory: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useStoryStore = create<StoryStore>((set) => ({
  stories: [],
  currentStory: null,
  isLoading: false,
  error: null,

  setStories: (stories) => set({ stories }),
  setCurrentStory: (story) => set({ currentStory: story }),
  addStory: (story) => set((state) => ({ stories: [...state.stories, story] })),
  updateStory: (story) =>
    set((state) => ({
      stories: state.stories.map((s) => (s.id === story.id ? story : s)),
      currentStory: state.currentStory?.id === story.id ? story : state.currentStory,
    })),
  removeStory: (id) =>
    set((state) => ({
      stories: state.stories.filter((s) => s.id !== id),
      currentStory: state.currentStory?.id === id ? null : state.currentStory,
    })),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));

interface PipelineStore {
  pipeline: PipelineState | null;
  isRunning: boolean;
  currentPhase: string | null;
  progress: number;

  setPipeline: (pipeline: PipelineState) => void;
  updateProgress: (progress: number) => void;
  setCurrentPhase: (phase: string) => void;
  clearPipeline: () => void;
}

export const usePipelineStore = create<PipelineStore>((set) => ({
  pipeline: null,
  isRunning: false,
  currentPhase: null,
  progress: 0,

  setPipeline: (pipeline) =>
    set({
      pipeline,
      isRunning: pipeline.status === 'running',
      currentPhase: pipeline.current_phase || null,
      progress: pipeline.progress.progress_percentage,
    }),
  updateProgress: (progress) => set({ progress }),
  setCurrentPhase: (phase) => set({ currentPhase: phase }),
  clearPipeline: () =>
    set({ pipeline: null, isRunning: false, currentPhase: null, progress: 0 }),
}));

interface EditorStore {
  // Editor state
  activeChapter: Chapter | null;
  chapters: Chapter[];
  characters: Character[];
  selectedCharacter: Character | null;
  showPreview: boolean;
  showMemoryBrowser: boolean;
  viewMode: 'edit' | 'preview' | 'split';

  // Actions
  setActiveChapter: (chapter: Chapter | null) => void;
  setChapters: (chapters: Chapter[]) => void;
  updateChapter: (chapter: Chapter) => void;
  setCharacters: (characters: Character[]) => void;
  setSelectedCharacter: (character: Character | null) => void;
  togglePreview: () => void;
  toggleMemoryBrowser: () => void;
  setViewMode: (mode: 'edit' | 'preview' | 'split') => void;
}

export const useEditorStore = create<EditorStore>((set) => ({
  activeChapter: null,
  chapters: [],
  characters: [],
  selectedCharacter: null,
  showPreview: true,
  showMemoryBrowser: false,
  viewMode: 'split',

  setActiveChapter: (chapter) => set({ activeChapter: chapter }),
  setChapters: (chapters) => set({ chapters }),
  updateChapter: (chapter) =>
    set((state) => ({
      chapters: state.chapters.map((c) => (c.id === chapter.id ? chapter : c)),
      activeChapter: state.activeChapter?.id === chapter.id ? chapter : state.activeChapter,
    })),
  setCharacters: (characters) => set({ characters }),
  setSelectedCharacter: (character) => set({ selectedCharacter: character }),
  togglePreview: () => set((state) => ({ showPreview: !state.showPreview })),
  toggleMemoryBrowser: () => set((state) => ({ showMemoryBrowser: !state.showMemoryBrowser })),
  setViewMode: (mode) => set({ viewMode: mode }),
}));

interface UIStore {
  // UI state
  sidebarOpen: boolean;
  theme: 'dark' | 'light';
  notifications: Array<{ id: string; message: string; type: 'info' | 'success' | 'warning' | 'error' }>;

  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  addNotification: (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  theme: 'dark',
  notifications: [],

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  addNotification: (message, type = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    set((state) => ({
      notifications: [...state.notifications, { id, message, type }],
    }));
    setTimeout(() => {
      set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
      }));
    }, 5000);
  },
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
