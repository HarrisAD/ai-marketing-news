import axios from 'axios';
import { Story, Newsletter, NewsSource, SystemStats, NewsletterRequest, AddSourceRequest, OpenAIConfigStatus } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 1 minute timeout - faster feedback for users
});

// Stories API
export const storiesApi = {
  getStories: async (params?: {
    min_score?: number;
    source_domain?: string;
    days_back?: number;
    limit?: number;
    canonical_only?: boolean;
    date_from?: string;
    date_to?: string;
  }): Promise<{ stories: Story[]; count: number }> => {
    const response = await api.get('/stories', { params });
    return response.data;
  },

  getStory: async (storyId: string): Promise<{ story: Story }> => {
    const response = await api.get(`/stories/${storyId}`);
    return response.data;
  },

  refreshStories: async (): Promise<any> => {
    const response = await api.post('/refresh');
    return response.data;
  },

  getSources: async (): Promise<{ sources: NewsSource[]; count: number }> => {
    const response = await api.get('/sources');
    return response.data;
  },

  updateSourceStatus: async (domain: string, active: boolean): Promise<any> => {
    const response = await api.post(`/sources/${encodeURIComponent(domain)}/status`, { active });
    return response.data;
  },

  addSource: async (request: AddSourceRequest): Promise<any> => {
    const response = await api.post('/sources', request);
    return response.data;
  },

  getTags: async (): Promise<{ tags: string[]; count: number }> => {
    const response = await api.get('/tags');
    return response.data;
  },

  getStats: async (): Promise<{ stats: SystemStats }> => {
    const response = await api.get('/stats');
    return response.data;
  },

  getOpenAIConfig: async (): Promise<OpenAIConfigStatus> => {
    const response = await api.get('/config/openai');
    return response.data;
  },

  updateOpenAIKey: async (apiKey: string): Promise<OpenAIConfigStatus> => {
    const response = await api.post('/config/openai', { api_key: apiKey });
    return response.data;
  },

  deleteStories: async (storyIds?: string[]): Promise<{ deleted: number }> => {
    const response = await api.post('/stories/delete', {
      story_ids: storyIds && storyIds.length ? storyIds : [],
    });
    return response.data;
  },

  getRefreshStatus: async (): Promise<any> => {
    const response = await api.get('/refresh/status');
    return response.data;
  },
};

// Newsletters API
export const newslettersApi = {
  generateNewsletter: async (request: NewsletterRequest): Promise<{ newsletter: Newsletter }> => {
    const response = await api.post('/newsletters/render', request);
    return response.data;
  },

  getNewsletters: async (): Promise<{ newsletters: Newsletter[]; count: number }> => {
    const response = await api.get('/newsletters');
    return response.data;
  },

  getNewsletter: async (newsletterId: string): Promise<{ newsletter: Newsletter }> => {
    const response = await api.get(`/newsletters/${newsletterId}`);
    return response.data;
  },

  downloadMarkdown: async (newsletterId: string): Promise<string> => {
    const response = await api.get(`/newsletters/${newsletterId}/markdown`, {
      responseType: 'text',
    });
    return response.data;
  },

  getNewsletterStories: async (newsletterId: string): Promise<{ stories: Story[]; count: number }> => {
    const response = await api.get(`/newsletters/${newsletterId}/stories`);
    return response.data;
  },

  getNewsletterAnalytics: async (newsletterId: string): Promise<any> => {
    const response = await api.get(`/newsletters/${newsletterId}/analytics`);
    return response.data;
  },
};

export default api;
