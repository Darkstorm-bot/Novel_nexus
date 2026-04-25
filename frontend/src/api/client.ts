import axios, { AxiosInstance, AxiosError } from 'axios';
import type { 
  Story, StoryCreate, StoryUpdate,
  Chapter, ChapterCreate, ChapterUpdate,
  Character, CharacterCreate,
  PipelineState,
  MemPalaceStatus,
  MemoryItem,
  LLMTestConfig,
  ConsistencyReport
} from '../types';

const API_BASE_URL = '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Story endpoints
  async getStories(): Promise<Story[]> {
    const response = await this.client.get<Story[]>('/stories');
    return response.data;
  }

  async getStory(id: string): Promise<Story> {
    const response = await this.client.get<Story>(`/stories/${id}`);
    return response.data;
  }

  async createStory(data: StoryCreate): Promise<Story> {
    const response = await this.client.post<Story>('/stories', data);
    return response.data;
  }

  async updateStory(id: string, data: StoryUpdate): Promise<Story> {
    const response = await this.client.put<Story>(`/stories/${id}`, data);
    return response.data;
  }

  async deleteStory(id: string): Promise<void> {
    await this.client.delete(`/stories/${id}`);
  }

  // Chapter endpoints
  async getChapters(storyId: string): Promise<Chapter[]> {
    const response = await this.client.get<Chapter[]>(`/stories/${storyId}/chapters`);
    return response.data;
  }

  async getChapter(storyId: string, chapterId: string): Promise<Chapter> {
    const response = await this.client.get<Chapter>(
      `/stories/${storyId}/chapters/${chapterId}`
    );
    return response.data;
  }

  async createChapter(storyId: string, data: ChapterCreate): Promise<Chapter> {
    const response = await this.client.post<Chapter>(
      `/stories/${storyId}/chapters`,
      data
    );
    return response.data;
  }

  async updateChapter(
    storyId: string,
    chapterId: string,
    data: ChapterUpdate
  ): Promise<Chapter> {
    const response = await this.client.put<Chapter>(
      `/stories/${storyId}/chapters/${chapterId}`,
      data
    );
    return response.data;
  }

  async deleteChapter(storyId: string, chapterId: string): Promise<void> {
    await this.client.delete(`/stories/${storyId}/chapters/${chapterId}`);
  }

  // Character endpoints
  async getCharacters(storyId: string): Promise<Character[]> {
    const response = await this.client.get<Character[]>(
      `/stories/${storyId}/characters`
    );
    return response.data;
  }

  async createCharacter(storyId: string, data: CharacterCreate): Promise<Character> {
    const response = await this.client.post<Character>(
      `/stories/${storyId}/characters`,
      data
    );
    return response.data;
  }

  async updateCharacter(
    storyId: string,
    characterId: string,
    data: Partial<CharacterCreate>
  ): Promise<Character> {
    const response = await this.client.put<Character>(
      `/stories/${storyId}/characters/${characterId}`,
      data
    );
    return response.data;
  }

  async deleteCharacter(storyId: string, characterId: string): Promise<void> {
    await this.client.delete(`/stories/${storyId}/characters/${characterId}`);
  }

  // Pipeline endpoints
  async getPipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.get<PipelineState>(
      `/stories/${storyId}/pipeline`
    );
    return response.data;
  }

  async startPipeline(storyId: string, config?: Record<string, any>): Promise<PipelineState> {
    const response = await this.client.post<PipelineState>(
      `/stories/${storyId}/pipeline/start`,
      config || {}
    );
    return response.data;
  }

  async pausePipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.post<PipelineState>(
      `/stories/${storyId}/pipeline/pause`
    );
    return response.data;
  }

  async resumePipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.post<PipelineState>(
      `/stories/${storyId}/pipeline/resume`
    );
    return response.data;
  }

  async approvePhase(storyId: string, phase: string): Promise<PipelineState> {
    const response = await this.client.post<PipelineState>(
      `/stories/${storyId}/pipeline/approve/${phase}`
    );
    return response.data;
  }

  async rejectPhase(
    storyId: string,
    phase: string,
    reason: string
  ): Promise<PipelineState> {
    const response = await this.client.post<PipelineState>(
      `/stories/${storyId}/pipeline/reject/${phase}`,
      { reason }
    );
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // MemPalace endpoints
  async getMemPalaceStatus(): Promise<MemPalaceStatus> {
    const response = await this.client.get<MemPalaceStatus>('/mempalace/status');
    return response.data;
  }

  async testLLMConnection(config: LLMTestConfig): Promise<any> {
    const response = await this.client.post('/mempalace/test-llm', config);
    return response.data;
  }

  async initializeMemPalace(config?: LLMTestConfig): Promise<any> {
    const response = await this.client.post('/mempalace/initialize', config || {});
    return response.data;
  }

  async storeMemory(
    collectionName: string,
    content: string,
    metadata?: Record<string, any>
  ): Promise<{ success: boolean; message: string }> {
    const response = await this.client.post('/mempalace/memory/store', {
      collection_name: collectionName,
      content,
      metadata
    });
    return response.data;
  }

  async searchMemories(
    collectionName: string,
    query: string,
    nResults: number = 5
  ): Promise<MemoryItem[]> {
    const response = await this.client.post('/mempalace/memory/search', {
      collection_name: collectionName,
      query,
      n_results: nResults
    });
    const data = response.data as { success: boolean; results: MemoryItem[] };
    return data.success ? data.results : [];
  }

  async checkConsistency(
    storyId: string,
    newContent: string,
    context?: string
  ): Promise<ConsistencyReport> {
    const response = await this.client.post('/mempalace/consistency/check', {
      story_id: storyId,
      new_content: newContent,
      context: context || null
    });
    const data = response.data as { success: boolean; report: ConsistencyReport };
    return data.report;
  }

  async extractEntities(
    storyId: string,
    content: string
  ): Promise<{ characters: string[]; locations: string[]; objects: string[] }> {
    const response = await this.client.post('/mempalace/entities/extract', {
      story_id: storyId,
      content
    });
    const data = response.data as { success: boolean; entities: any };
    return data.entities;
  }

  async debugConnection(config: LLMTestConfig): Promise<any> {
    const response = await this.client.post('/mempalace/debug/connection', config);
    return response.data;
  }
}

export const api = new ApiClient();
export default api;
