// Story types
export interface Story {
  id: string;
  title: string;
  description?: string;
  genre?: string;
  tags: string[];
  status: 'draft' | 'in_progress' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
  chapter_count: number;
  word_count: number;
}

export interface StoryCreate {
  title: string;
  description?: string;
  genre?: string;
  tags?: string[];
}

export interface StoryUpdate {
  title?: string;
  description?: string;
  genre?: string;
  tags?: string[];
  status?: 'draft' | 'in_progress' | 'completed' | 'archived';
}

// Chapter types
export interface Chapter {
  id: string;
  story_id: string;
  title: string;
  summary?: string;
  order: number;
  content?: string;
  word_count: number;
  created_at: string;
  updated_at: string;
  scene_ids: string[];
}

export interface ChapterCreate {
  story_id: string;
  title: string;
  summary?: string;
  order: number;
}

export interface ChapterUpdate {
  title?: string;
  summary?: string;
  order?: number;
  content?: string;
}

// Character types
export interface CharacterState {
  location?: string;
  emotional_state?: string;
  goals: string[];
  conflicts: string[];
  relationships: Record<string, string>;
  last_seen_chapter?: string;
  metadata: Record<string, any>;
}

export interface Character {
  id: string;
  story_id: string;
  name: string;
  description?: string;
  role: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  background?: string;
  traits: string[];
  motivations: string[];
  state: CharacterState;
  created_at: string;
  updated_at: string;
  appearance_count: number;
}

export interface CharacterCreate {
  story_id: string;
  name: string;
  description?: string;
  role?: 'protagonist' | 'antagonist' | 'supporting' | 'minor';
  background?: string;
  traits?: string[];
  motivations?: string[];
}

// Pipeline types
export type PipelinePhase = 
  | 'concept' 
  | 'outline' 
  | 'beat_sheet' 
  | 'drafting' 
  | 'critique' 
  | 'rewrite' 
  | 'polish' 
  | 'consistency' 
  | 'export';

export type PipelineStatus = 
  | 'pending' 
  | 'running' 
  | 'waiting_approval' 
  | 'completed' 
  | 'failed' 
  | 'paused';

export interface PhaseResult {
  phase: PipelinePhase;
  status: string;
  output: Record<string, any>;
  errors: string[];
  requires_approval: boolean;
  approval_status?: string;
  completed_at?: string;
}

export interface PipelineProgress {
  current_phase: PipelinePhase;
  overall_status: PipelineStatus;
  phase_results: Record<PipelinePhase, PhaseResult>;
  started_at?: string;
  completed_at?: string;
  progress_percentage: number;
  current_step?: string;
  total_steps: number;
  completed_steps: number;
}

export interface PipelineState {
  id: string;
  story_id: string;
  status: PipelineStatus;
  current_phase?: PipelinePhase;
  progress: PipelineProgress;
  config: Record<string, any>;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  checkpoint_data?: Record<string, any>;
}

// Memory types
export interface MemoryItem {
  id: string;
  content: string;
  metadata: Record<string, any>;
  embedding?: number[];
  created_at: string;
}

export interface VectorSearchResult {
  item: MemoryItem;
  score: number;
}

// WebSocket message types
export interface WSMessage {
  type: 'pipeline_update' | 'story_update' | 'character_update' | 'memory_update' | 'error';
  payload: any;
  timestamp: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Diff types
export interface ContentDiff {
  original: string;
  modified: string;
  changes: Array<{
    type: 'add' | 'remove' | 'unchanged';
    value: string;
  }>;
}
