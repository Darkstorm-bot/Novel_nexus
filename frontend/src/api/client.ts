import axios, { AxiosInstance, AxiosError } from 'axios';
import type { 
  Story, StoryCreate, StoryUpdate,
  Chapter, ChapterCreate, ChapterUpdate,
  Character, CharacterCreate,
  PipelineState,
  ApiResponse, PaginatedResponse 
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
  async getStories(): Promise<PaginatedResponse<Story>> {
    const response = await this.client.get<ApiResponse<PaginatedResponse<Story>>>('/stories');
    return response.data.data;
  }

  async getStory(id: string): Promise<Story> {
    const response = await this.client.get<ApiResponse<Story>>(`/stories/${id}`);
    return response.data.data;
  }

  async createStory(data: StoryCreate): Promise<Story> {
    const response = await this.client.post<ApiResponse<Story>>('/stories', data);
    return response.data.data;
  }

  async updateStory(id: string, data: StoryUpdate): Promise<Story> {
    const response = await this.client.put<ApiResponse<Story>>(`/stories/${id}`, data);
    return response.data.data;
  }

  async deleteStory(id: string): Promise<void> {
    await this.client.delete(`/stories/${id}`);
  }

  // Chapter endpoints
  async getChapters(storyId: string): Promise<Chapter[]> {
    const response = await this.client.get<ApiResponse<Chapter[]>>(`/stories/${storyId}/chapters`);
    return response.data.data;
  }

  async getChapter(storyId: string, chapterId: string): Promise<Chapter> {
    const response = await this.client.get<ApiResponse<Chapter>>(
      `/stories/${storyId}/chapters/${chapterId}`
    );
    return response.data.data;
  }

  async createChapter(storyId: string, data: ChapterCreate): Promise<Chapter> {
    const response = await this.client.post<ApiResponse<Chapter>>(
      `/stories/${storyId}/chapters`,
      data
    );
    return response.data.data;
  }

  async updateChapter(
    storyId: string,
    chapterId: string,
    data: ChapterUpdate
  ): Promise<Chapter> {
    const response = await this.client.put<ApiResponse<Chapter>>(
      `/stories/${storyId}/chapters/${chapterId}`,
      data
    );
    return response.data.data;
  }

  async deleteChapter(storyId: string, chapterId: string): Promise<void> {
    await this.client.delete(`/stories/${storyId}/chapters/${chapterId}`);
  }

  // Character endpoints
  async getCharacters(storyId: string): Promise<Character[]> {
    const response = await this.client.get<ApiResponse<Character[]>>(
      `/stories/${storyId}/characters`
    );
    return response.data.data;
  }

  async createCharacter(storyId: string, data: CharacterCreate): Promise<Character> {
    const response = await this.client.post<ApiResponse<Character>>(
      `/stories/${storyId}/characters`,
      data
    );
    return response.data.data;
  }

  async updateCharacter(
    storyId: string,
    characterId: string,
    data: Partial<CharacterCreate>
  ): Promise<Character> {
    const response = await this.client.put<ApiResponse<Character>>(
      `/stories/${storyId}/characters/${characterId}`,
      data
    );
    return response.data.data;
  }

  async deleteCharacter(storyId: string, characterId: string): Promise<void> {
    await this.client.delete(`/stories/${storyId}/characters/${characterId}`);
  }

  // Pipeline endpoints
  async getPipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.get<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline`
    );
    return response.data.data;
  }

  async startPipeline(storyId: string, config?: Record<string, any>): Promise<PipelineState> {
    const response = await this.client.post<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline/start`,
      config
    );
    return response.data.data;
  }

  async pausePipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.post<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline/pause`
    );
    return response.data.data;
  }

  async resumePipeline(storyId: string): Promise<PipelineState> {
    const response = await this.client.post<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline/resume`
    );
    return response.data.data;
  }

  async approvePhase(storyId: string, phase: string): Promise<PipelineState> {
    const response = await this.client.post<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline/approve/${phase}`
    );
    return response.data.data;
  }

  async rejectPhase(
    storyId: string,
    phase: string,
    reason: string
  ): Promise<PipelineState> {
    const response = await this.client.post<ApiResponse<PipelineState>>(
      `/stories/${storyId}/pipeline/reject/${phase}`,
      { reason }
    );
    return response.data.data;
  }

  // Health check
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new ApiClient();
export default api;
